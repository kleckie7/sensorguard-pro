# SensorGuard Pro

**eVTOL Aircraft Sensor Cybersecurity Assessment Prototype**

![SensorGuard Pro Dashboard in Action](screenshot.png)

A Python-based simulation tool that assesses cybersecurity threats across ~162 redundant sensors in an eVTOL aircraft.

Demonstrates real-time detection of spoofing, tampering, integrity breaches, and anomalies.

## Demo

![SensorGuard Pro Dashboard](screenshot.png)

## Features
- Realistic sensor simulation with redundancy
- Dynamic breach injection — different every run
- 5-phase cybersecurity methodology
- Interactive Tkinter dashboard with color-coded alerts
- Detailed logging (cleared per run)

## How to Run
```bash
git clone https://github.com/kleckie7/sensorguard-pro.git
cd sensorguard-pro
python3 main.py