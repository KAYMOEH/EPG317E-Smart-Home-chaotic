
---

# 🏠 EPG317E Capstone: IoT Smart Home System

**Department of Electrical, Electronic & Computer Engineering** **Central University of Technology, Free State**

## 1. Project Overview

Our team has engineered a real-time IoT Smart Home ecosystem using an **ESP32 microcontroller** and the Keyestudio KS0085 kit. The system operates as a **cloud-deployed application**, bridging the gap between local sensor data and a globally reachable web interface. By deploying to a remote, always-available environment, we ensure the system is reachable on a public URL rather than just a local machine.

**Live Dashboard:** [https://huggingface.co/spaces/Kaymoeh/iot-smart-home-dashboard]

## 2. The Team

* **Kamogelo Motshwene** – Lead Firmware Developer
* **Mbalenhle Mahlangu** – Embedded Systems Specialist
* **Memory Moyo** – Backend & Database Engineer
* **Phiwokuhle Mpumelelo Hlongwane** – Integration & Deployment Lead

## 3. System Architecture

We have transitioned from local scripts to a **Platform as a Service (PaaS)** model. This allows our sensors to run continuously and our backend to ingest MQTT messages around the clock.

* **Hardware Layer:** ESP32 reads environment and security sensors and publishes data to MQTT topics.
* **Transport Layer:** MQTT protocol transmits JSON payloads via a broker to route messages between the home and the cloud.
* **Backend (PaaS):** A Python-based service manages a **SQLite database** and runs a persistent subscriber to log incoming data.
* **Application Layer:** A **Panel dashboard** served via a **WSGI server** translates HTTP requests into a Python call, producing a response for the user's browser.

## 4. Hardware & Pin Mapping

| Component | ESP32 GPIO | Type | Logic Description |
| --- | --- | --- | --- |
| **White LED** | 13 | Digital | Automatic night lighting (Photocell-triggered) |
| **Yellow LED** | 12 | PWM | Motion indicator with remote brightness control |
| **Photocell** | 33 | Analog | Measures ambient light intensity |
| **Steam Sensor** | 25 | Analog | Detects rain to trigger window closure |
| **MQ-2 Sensor** | 26 | Analog | Gas leak detection (High Priority Alert) |
| **PIR Sensor** | 27 | Digital | Human motion detection for security |
| **Window Servo** | 18 | PWM | Autonomous/manual ventilation control |
| **Door Servo** | 15 | PWM | Security-locked entrance control |
| **Fan** | 32 / 23 | Digital | Ventilation for high gas or temperature |
| **Relay** | 14 | Digital | Emergency power cutoff for appliances |
| **Buzzer** | 19 | Digital | 5-second acoustic alarm for gas/motion |
| **LCD** | 21 / 22 | I2C | Real-time status and event display |

## 5. Deployment & Environment

To ensure **reproducibility**, this project uses isolated environments:

* **Virtual Environments:** Each deployment target uses a `venv` (a folder containing its own copy of Python and pip) to prevent dependency conflicts.
* **Manifest:** The `requirements.txt` file pins exact versions of packages to ensure the app runs the same way in the cloud as it does on a developer's machine.
* **Docker:** Used on platforms like Hugging Face to bundle code, configuration, and networking together in a containerized environment.

## 6. GitHub Workflow

We follow an industry-standard **Feature Branch + Pull Request** workflow:

1. **main:** Production-ready code only.
2. **Branches:** Development occurs on specific task branches (e.g., `feature/gas-priority-logic`).
3. **Reviews:** All code must be reviewed and approved by at least one other team member before merging into main to ensure quality.

## 7. Setup & Installation

1. **Clone:** `git clone [https://github.com/KAYMOEH/EPG317E-Smart-Home-chaotic.git]`.
2. **Environment:** `python -m venv venv` and `source venv/bin/activate`.
3. **Dependencies:** `pip install -r requirements.txt`.
4. **Database:** Run `python web_app/database.py` to initialize the SQLite schema.
5. **Run:** Launch `app.py` locally or deploy via a **PaaS Web Dashboard**.