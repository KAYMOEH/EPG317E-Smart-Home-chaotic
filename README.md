# EPG317E Capstone Project: IoT Smart Home Monitoring & Control Dashboard

**Central University of Technology, Free State** **Department of Electrical, Electronic and Computer Engineering** ---

## 1. Project Overview
Our team has designed and deployed a real-time **IoT Smart Home** system using the Keyestudio KS0085 kit, modified with an **ESP32** microcontroller. The system collects environmental data, transmits it via **MQTT**, logs it into a **SQLite database**, and displays it on a professional **Python Panel dashboard** hosted on **PythonAnywhere**.

**Live Dashboard Link:** [Insert your PythonAnywhere URL here]

---

## 2. The Team
* **Kamogelo Motshwene** – Lead Firmware Developer
* **Mbalenhle Mahlangu** – Embedded Systems Specialist
* **Memory Moyo** – Backend & Database Engineer
* **Ntsikelelo Mvambo** – Dashboard Developer
* **Phiwokuhle Mpumelelo Hlongwane** – Integration & Deployment Lead

---

## 3. System Architecture
[cite_start]The data flow of our Smart Home follows this pipeline[cite: 1]:
1. [cite_start]**ESP32 (C++)**: Reads sensors and publishes data to MQTT topics[cite: 1].
2. **MQTT Broker**: Routes messages between the home and the cloud.
3. **Python Subscriber**: A script on PythonAnywhere that saves incoming data to **SQLite**.
4. **Panel Dashboard**: Displays live readings, historical plots, and sends control commands.

---

## 4. Hardware & Pin Mapping
Since this kit originally used an Arduino board, we have remapped the following components to the **ESP32 GPIOs**:

| Component | Original Arduino Pin | ESP32 GPIO | Type |
| :--- | :--- | :--- | :--- |
| **White LED** | D13 | **GPIO 13** | Digital |
| **Yellow LED** | D12 | **GPIO 12** | PWM |
| **Photocell (Light)** | A0 | **GPIO 33** | Analog |
| **Steam (Rain)** | A3 | **GPIO 25** | Analog |
| **MQ-2 (Gas)** | A2 | **GPIO 26** | Analog |
| **PIR (Motion)** | D2 | **GPIO 27** | Digital |
| **Window Servo** | D9 | **GPIO 18** | PWM |
| **Door Servo** | D10 | **GPIO 15** | PWM |
| **Fan (INA/INB)** | D5/D6 | **GPIO 32 / 23** | Digital/PWM |
| **Relay** | D4 | **GPIO 14** | Digital |
| **Buzzer** | D3 | **GPIO 19** | Digital |
| **I2C LCD** | SDA/SCL | **GPIO 21 / 22** | I2C |

---

## 5. MQTT Topic Structure
We use the following structured naming convention for communication:

### Sensors (Publish)
* `epg317e/home/<team_id>/sensors/light`
* `epg317e/home/<team_id>/sensors/gas`
* `epg317e/home/<team_id>/sensors/motion`
* `epg317e/home/<team_id>/sensors/rain`

### Actuators (Subscribe/Control)
* `epg317e/home/<team_id>/control/door`
* `epg317e/home/<team_id>/control/window`
* `epg317e/home/<team_id>/control/fan`
* `epg317e/home/<team_id>/control/led_yellow`

---

## 6. GitHub Workflow
To maintain code quality, our team follows a **Feature Branch + Pull Request** workflow:
* **`main`**: Contains stable, production-ready code.
* **Feature Branches**: Created for specific tasks (e.g., `feature/mqtt-setup`).
* **Pull Requests**: All code must be reviewed and approved by at least one other team member before merging into `main`.
* **Contributions**: Each member is responsible for a minimum of 3 meaningful PRs.

---

## 7. Setup & Installation
1. **Firmware**: Flash the `.ino` file in the `/firmware` folder using the Arduino IDE.
2. **Database**: Run `init_db.py` to create the SQLite tables.
3. **Dashboard**: Install dependencies via `pip install -r requirements.txt` and run `app.py`.
