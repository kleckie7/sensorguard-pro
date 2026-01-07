import json
import os
import random
import hashlib
import logging
import tkinter as tk
from tkinter import ttk
import threading

# Define sensor categories with redundancy (total ~162 sensors)
SENSOR_CATEGORIES = {
    "Air Data and Wind-Related": [
        {"type": "Pitot-static probe", "redundancy": 4},
        {"type": "Angle of Attack (AOA) vane", "redundancy": 3},
        {"type": "Angle of Sideslip (AOS)", "redundancy": 3},
        {"type": "Total Air Temperature (TAT) probe", "redundancy": 2},
        {"type": "Air Data Module (ADM)", "redundancy": 4},
        {"type": "Ultrasonic wind sensor", "redundancy": 2}
    ],
    "Speed and Velocity": [
        {"type": "Airspeed indicator (derived)", "redundancy": 3},
        {"type": "Ground speed (GNSS Doppler)", "redundancy": 2},
        {"type": "Inertial speed (from IMU)", "redundancy": 4}
    ],
    "Flight Control and Attitude": [
        {"type": "Inertial Measurement Unit (IMU)", "redundancy": 6},
        {"type": "Magnetometer", "redundancy": 3},
        {"type": "Barometric pressure sensor", "redundancy": 4}
    ],
    "Navigation and Positioning": [
        {"type": "GNSS/GPS receiver", "redundancy": 4},
        {"type": "Radar/Laser altimeter", "redundancy": 3}
    ],
    "Propulsion and Powertrain": [
        {"type": "Motor resolver/position sensor", "redundancy": 12},
        {"type": "Current/voltage sensor", "redundancy": 12},
        {"type": "Temperature sensor", "redundancy": 24},
        {"type": "Vibration sensor", "redundancy": 12}
    ],
    "Perception and Obstacle Avoidance": [
        {"type": "LIDAR unit", "redundancy": 4},
        {"type": "Radar (mm-wave)", "redundancy": 3},
        {"type": "Camera (EO/IR)", "redundancy": 6},
        {"type": "Ultrasonic sensor", "redundancy": 4}
    ]
}

def generate_sensor_config():
    sensors = []
    sensor_id = 1
    for category, items in SENSOR_CATEGORIES.items():
        for item in items:
            for r in range(item["redundancy"]):
                sensors.append({
                    "id": sensor_id,
                    "type": item["type"],
                    "category": category,
                    "status": "Nominal",
                    "data": None,
                    "hash": None
                })
                sensor_id += 1
    with open('sensors.json', 'w') as f:
        json.dump(sensors, f)
    return sensors

if not os.path.exists('sensors.json'):
    sensors = generate_sensor_config()
else:
    with open('sensors.json', 'r') as f:
        sensors = json.load(f)

logging.basicConfig(filename='test_logs.txt', level=logging.INFO, force=True, 
                    format='%(asctime)s - %(message)s')

def simulate_sensor_data(sensor):
    if "Airspeed" in sensor["type"] or "speed" in sensor["type"]:
        sensor["data"] = random.uniform(0, 300)
    elif "Temperature" in sensor["type"]:
        sensor["data"] = random.uniform(20, 100)
    elif "IMU" in sensor["type"]:
        sensor["data"] = [random.uniform(-1, 1) for _ in range(3)]
    else:
        sensor["data"] = random.uniform(0, 100)
    sensor["hash"] = hashlib.sha256(str(sensor["data"]).encode()).hexdigest()

def inject_breaches(sensors, breach_rate=0.1):
    for sensor in sensors:
        if random.random() < breach_rate:
            if random.choice([True, False]):
                sensor["data"] = sensor["data"] * random.uniform(1.5, 2.0)
                sensor["status"] = "Spoofed"
            else:
                sensor["hash"] = hashlib.sha256(str(random.random()).encode()).hexdigest()
                sensor["status"] = "Tampered"
            logging.info(f"Breach injected in {sensor['type']} ID {sensor['id']}: {sensor['status']}")

# Simulate data and inject breaches
for sensor in sensors:
    simulate_sensor_data(sensor)
inject_breaches(sensors)

def assess_sensors(sensors):
    results = {"nominal": 0, "breached": 0, "mitigated": 0}
    for sensor in sensors:
        risk_level = "High" if sensor["category"] in ["Air Data and Wind-Related", "Flight Control and Attitude", "Navigation and Positioning"] else "Medium"
        
        expected_hash = hashlib.sha256(str(sensor["data"]).encode()).hexdigest()
        if sensor["hash"] != expected_hash:
            sensor["status"] = "Integrity Breach"
            results["breached"] += 1
        else:
            if isinstance(sensor["data"], list):
                if any(abs(val) > 0.8 for val in sensor["data"]):
                    sensor["status"] = "Anomaly Detected"
                    results["breached"] += 1
            elif sensor["data"] > 150:
                sensor["status"] = "Anomaly Detected"
                results["breached"] += 1
            else:
                sensor["status"] = "Nominal"
                results["nominal"] += 1
        
        if "Breached" in sensor["status"] or "Detected" in sensor["status"] or "Spoofed" in sensor["status"] or "Tampered" in sensor["status"]:
            sensor["status"] += " - Failover Activated"
            results["mitigated"] += 1
        
        logging.info(f"{sensor['type']} ID {sensor['id']}: {sensor['status']} (Risk: {risk_level})")
    
    return results

def run_assessment():
    results = assess_sensors(sensors)
    status_label.config(text=f"Nominal: {results['nominal']} | Breached: {results['breached']} | Mitigated: {results['mitigated']}")
    tree.delete(*tree.get_children())
    for sensor in sensors:
        tag = "red" if "Breached" in sensor["status"] or "Detected" in sensor["status"] else "green"
        tree.insert("", "end", values=(sensor["id"], sensor["type"], sensor["category"], sensor["status"]), tags=(tag,))

def start_gui():
    root = tk.Tk()
    root.title("SensorGuard Pro Dashboard - eVTOL Sensor Assessment")
    root.geometry("1000x700")
    root.configure(bg="#f0f0f0")

    global status_label
    status_label = tk.Label(root, text="Press 'Run Test' to Assess 162 Sensors", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
    status_label.pack(pady=20)

    global tree
    tree = ttk.Treeview(root, columns=("ID", "Type", "Category", "Status"), show="headings", height=20)
    tree.heading("ID", text="ID")
    tree.heading("Type", text="Sensor Type")
    tree.heading("Category", text="Category")
    tree.heading("Status", text="Status")
    tree.column("ID", width=60, anchor="center")
    tree.column("Type", width=300)
    tree.column("Category", width=250)
    tree.column("Status", width=350)
    tree.pack(padx=20, pady=10, fill="both", expand=True)

    tree.tag_configure("red", foreground="red", font=("Helvetica", 10, "bold"))
    tree.tag_configure("green", foreground="darkgreen")

    button_frame = tk.Frame(root, bg="#f0f0f0")
    button_frame.pack(pady=10)

    test_button = tk.Button(button_frame, text="Run Full Sensor Test", font=("Helvetica", 14), padx=20, pady=10, command=run_assessment)
    test_button.pack(side="left", padx=10)

    log_button = tk.Button(button_frame, text="Open Test Logs", font=("Helvetica", 14), padx=20, pady=10, 
                           command=lambda: os.system("open test_logs.txt"))
    log_button.pack(side="left", padx=10)

    root.mainloop()

# Launch GUI directly on the main thread (fixes macOS crash)
if __name__ == "__main__":
    start_gui()