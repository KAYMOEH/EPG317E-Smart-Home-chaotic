# EPG317E — Engineering Programming III  
# Capstone Project: IoT Smart Home Monitoring & Control Dashboard

**Central University of Technology, Free State**  
**Department of Electrical, Electronic and Computer Engineering**  

---

## 1. Project Overview

Your team will design, build, and deploy a **real-time IoT monitoring and control dashboard** for the **Keyestudio Smart Home Kit (KS0085)**, modified to use an **ESP32** microcontroller. The ESP32 will collect sensor data from the kit's home automation sensors, publish it via **MQTT** to a cloud broker, and receive control instructions from a **Panel (Python)** web dashboard. All sensor data will be stored in a **SQLite** database and the dashboard will be deployed on **PythonAnywhere**.

This project integrates embedded systems programming (C/C++ on ESP32), IoT communication protocols (MQTT), data storage (SQLite), data visualisation (Panel/HoloViz), and web deployment — skills that are directly applicable to modern engineering practice, particularly in home automation and building management systems.

### 1.1 Learning Outcomes

Upon completion of this project, students will be able to:

- Program an ESP32 microcontroller to read sensors and communicate over Wi-Fi using MQTT.
- Design and implement an MQTT topic structure for a multi-sensor IoT system.
- Build a real-time web dashboard using Python Panel that displays live and historical data.
- Store time-series sensor data in a SQLite database and query it for visualisation.
- Deploy a Python web application on PythonAnywhere.
- Collaborate effectively using Git, GitHub, feature branches, and pull requests.
- Document and present a technical engineering project professionally.

---

## 2. Your Kit — Keyestudio Smart Home Kit (KS0085)

<img src="https://m.media-amazon.com/images/I/71W5DF0wVyL._AC_UF1000,1000_QL80_.jpg" alt="Keyestudio Smart Home Kit (KS0085)" width="400"/>

**Kit Documentation:** [https://wiki.keyestudio.com/KS0085_Keyestudio_Smart_Home_Kit_for_Arduino](https://wiki.keyestudio.com/KS0085_Keyestudio_Smart_Home_Kit_for_Arduino)

> **Note:** The original Arduino PLUS control board included in this kit has been replaced with an **ESP32** development board to enable Wi-Fi and MQTT connectivity. You will need to adapt pin assignments accordingly.

### 2.1 Key Components

| Component | Purpose | Interface |
|-----------|---------|-----------|
| ESP32 Development Board | Main controller with Wi-Fi/Bluetooth (replaces Arduino PLUS) | — |
| Sensor Expansion Shield | Easy wiring of sensors to controller | Stacking |
| White LED Module | Room lighting control | Digital |
| Yellow LED Module | Secondary lighting / indicator | Digital (PWM capable) |
| Passive Buzzer | Alarm / doorbell / alerts | Digital |
| Button Module × 2 | User input (doorbell, password entry) | Digital |
| 1-Channel Relay Module | Switch high-current appliances | Digital |
| Photocell Sensor (Photoresistor) | Ambient light detection | Analog |
| Servo Motor × 2 | Door and window control | PWM |
| Fan Module (L9110) | Ventilation / cooling | Digital (2 pins: INA, INB) |
| Steam Sensor | Rain / moisture detection | Analog |
| PIR Motion Sensor | Human presence detection | Digital |
| MQ-2 Gas Sensor (Analog) | Flammable gas / smoke detection | Analog + Digital |
| I2C 1602 LCD Display | Local status display | I2C (SDA/SCL) |
| Soil Humidity Sensor | Plant watering monitoring | Analog |

### 2.2 Suggested Sensor Data to Collect

Your ESP32 firmware should read and publish (at minimum) the following data over MQTT:

- **Ambient light** level from photocell sensor (analog value)
- **Gas/smoke concentration** from MQ-2 sensor (analog value)
- **Motion detection** from PIR sensor (binary: detected / not detected)
- **Rain/moisture** level from steam sensor (analog value)
- **Soil moisture** level from soil humidity sensor (analog value)
- **Door servo angle** — current position (degrees)
- **Window servo angle** — current position (degrees)
- **Fan status** (on/off and direction)
- **Relay status** (connected/disconnected)
- **LED status** (on/off for both white and yellow LEDs)

### 2.3 Suggested Control Actions (Dashboard → ESP32)

Your dashboard should be able to send the following commands to the ESP32 via MQTT:

- **Open/close door** — control door servo (set angle 0°–180°)
- **Open/close window** — control window servo (set angle 0°–180°)
- **Toggle fan** on/off (and direction: forward/reverse)
- **Toggle relay** — switch external appliance on/off
- **Toggle white LED** on/off
- **Toggle/dim yellow LED** — on/off or PWM brightness
- **Trigger buzzer** — doorbell or alarm sound
- **Set gas alarm threshold** — analog value above which alarm activates
- **Arm/disarm motion detection** — enable/disable PIR-based security alerts

---

## 3. Technical Requirements

### 3.1 ESP32 Firmware (Arduino IDE / C++)

- Program the ESP32 using the **Arduino IDE**.
- Connect to Wi-Fi and an **MQTT broker** of your team's choice (any free broker is acceptable, e.g., HiveMQ Cloud, Mosquitto test broker, EMQX Cloud, etc.).
- Publish sensor data to structured MQTT topics at a regular interval (e.g., every 5–10 seconds).
- Subscribe to control topics and execute commands received from the dashboard.
- Design a clear **MQTT topic structure**, for example:
  ```
  epg317e/home/<team_id>/sensors/light
  epg317e/home/<team_id>/sensors/gas
  epg317e/home/<team_id>/sensors/motion
  epg317e/home/<team_id>/sensors/rain
  epg317e/home/<team_id>/sensors/soil_moisture
  epg317e/home/<team_id>/actuators/door_angle
  epg317e/home/<team_id>/actuators/window_angle
  epg317e/home/<team_id>/actuators/fan_status
  epg317e/home/<team_id>/actuators/relay_status
  epg317e/home/<team_id>/control/door
  epg317e/home/<team_id>/control/window
  epg317e/home/<team_id>/control/fan
  epg317e/home/<team_id>/control/relay
  epg317e/home/<team_id>/control/led_white
  epg317e/home/<team_id>/control/led_yellow
  epg317e/home/<team_id>/control/buzzer
  epg317e/home/<team_id>/control/gas_threshold
  epg317e/home/<team_id>/control/motion_armed
  ```

**Download Arduino IDE:** [https://www.arduino.cc/en/software](https://www.arduino.cc/en/software)

**ESP32 Board Setup for Arduino IDE:** Follow the official Espressif guide to add the ESP32 board package:  
[https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)

> **Important — Pin Mapping:** Since this kit was originally designed for the Arduino PLUS board, you will need to remap pins to the ESP32. Refer to your ESP32 board's pinout diagram and note that some Arduino analog pins (A0–A5) correspond to different ESP32 GPIO numbers. Document your pin mapping in the portfolio.

### 3.2 MQTT Broker

- Use **any free MQTT broker** of your choice.
- Popular options include:
  - [HiveMQ Cloud](https://www.hivemq.com/mqtt-cloud-broker/) (free tier)
  - [EMQX Cloud](https://www.emqx.com/en/cloud) (free tier)
  - [Mosquitto Test Broker](https://test.mosquitto.org/)
- Document your broker choice, connection details, and topic structure in your portfolio.

### 3.3 Python Dashboard (Panel / HoloViz)

Build a web-based dashboard using **Panel** ([https://panel.holoviz.org/](https://panel.holoviz.org/)) that provides:

**Live Data Display:**
- Real-time readings of all sensors (light level, gas concentration, rain, soil moisture).
- Motion detection alert indicator (with timestamp of last detection).
- Door and window status (open/closed with angle).
- Fan, relay, and LED status indicators.
- Gas level with alarm state (safe / warning / danger colour coding).
- Timestamps for the most recent data received.

**Historical Data Display:**
- Time-series plots (line charts) of gas levels, light levels, rain/moisture, and soil moisture over selectable time ranges (last 1 hour, 6 hours, 24 hours, 7 days).
- Motion event log (table showing timestamps of motion detections).
- Gas alarm event log (timestamps when gas exceeded threshold).
- Use **Matplotlib**, **hvPlot**, or **Bokeh** (all compatible with Panel) for plotting.

**Control Panel:**
- Buttons/toggles to send MQTT commands to the ESP32 (door, window, fan, relay, LEDs, buzzer, motion arm/disarm).
- Sliders for servo angles (door and window) and gas alarm threshold.
- Brightness slider for yellow LED (PWM control).

**Dashboard Quality:**
- Clean, professional layout with clear labels, units, and colour coding.
- Responsive to data updates.
- Error handling for lost MQTT connections.

### 3.4 Database (SQLite)

- Use **SQLite** to store all incoming sensor data with timestamps.
- Design an appropriate database schema (e.g., a table per sensor type or a single table with a sensor type column).
- The dashboard must query the database for historical data display.
- Include a script or mechanism to initialise the database schema.

### 3.5 Deployment (PythonAnywhere)

- Deploy your Panel dashboard on **PythonAnywhere** using a **free-tier account** (register at [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/)).
- The dashboard must be accessible via a public URL for demonstration and assessment.
- Document the deployment steps in your portfolio.

---

## 4. GitHub & Version Control Requirements

### 4.1 Repository Setup

- Create a **single GitHub repository** per team.
- The repository must be set to **public** (or grant the instructor access if private).
- Include a well-written `README.md` with:
  - Project title and description
  - Team members and student numbers
  - Setup and installation instructions
  - MQTT topic structure documentation
  - ESP32 pin mapping table (original Arduino pin → ESP32 GPIO)
  - Link to deployed dashboard
  - Wiring diagram or photo of the assembled kit

### 4.2 Branching Strategy — Feature Branches + Pull Requests

Your team must follow a **feature branch** workflow:

1. The `main` branch always contains working, tested code.
2. Each team member creates a **feature branch** from `main` for each task they work on. Branch names should be descriptive, e.g.:
   - `feature/mqtt-connection`
   - `feature/gas-sensor-reading`
   - `feature/dashboard-layout`
   - `feature/database-schema`
   - `feature/door-servo-control`
   - `feature/motion-detection-alerts`
   - `fix/lcd-display-bug`
3. When a feature is complete, the team member opens a **Pull Request (PR)** to merge into `main`.
4. At least **one other team member** must review and approve the PR before merging.
5. **Individual contributions will be assessed based on pull requests.** Each member must have meaningful PRs that demonstrate their contribution to the codebase.

### 4.3 Minimum Contribution Expectations

- Every team member must have **at least 3 meaningful pull requests** merged into `main`.
- PRs must contain real, substantive work — not trivial changes like fixing typos or reformatting.
- Commit messages must be clear and descriptive.
- The PR description should explain what was changed and why.

---

## 5. Assessment

Refer to the [README.md](README.md) for the full assessment rubrics (Code, Presentation & Demo).

> **Project-specific note:** The firmware rubric criterion also covers correct ESP32 pin remapping from the original Arduino PLUS board.

---

## 6. Resources & Links

### Software Downloads
- **Arduino IDE:** [https://www.arduino.cc/en/software](https://www.arduino.cc/en/software)
- **ESP32 Arduino Core Installation:** [https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
- **Python (3.10+):** [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Git:** [https://git-scm.com/downloads](https://git-scm.com/downloads)


### Documentation
- **Panel (HoloViz):** [https://panel.holoviz.org/](https://panel.holoviz.org/)
- **Paho MQTT (Python):** [https://pypi.org/project/paho-mqtt/](https://pypi.org/project/paho-mqtt/)
- **PubSubClient (ESP32 Arduino MQTT):** [https://github.com/knolleary/pubsubclient](https://github.com/knolleary/pubsubclient)
- **SQLite with Python:** [https://docs.python.org/3/library/sqlite3.html](https://docs.python.org/3/library/sqlite3.html)
- **PythonAnywhere:** [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/)
- **GitHub Docs — Pull Requests:** [https://docs.github.com/en/pull-requests](https://docs.github.com/en/pull-requests)

### Kit Resources
- **KS0085 Smart Home Kit Documentation:** [https://wiki.keyestudio.com/KS0085_Keyestudio_Smart_Home_Kit_for_Arduino](https://wiki.keyestudio.com/KS0085_Keyestudio_Smart_Home_Kit_for_Arduino)
- **Kit Code & Libraries Download:** [https://fs.keyestudio.com/KS0085](https://fs.keyestudio.com/KS0085)

### MQTT Brokers (Free Tier)
- **HiveMQ Cloud:** [https://www.hivemq.com/mqtt-cloud-broker/](https://www.hivemq.com/mqtt-cloud-broker/)
- **EMQX Cloud:** [https://www.emqx.com/en/cloud](https://www.emqx.com/en/cloud)
- **Mosquitto Test Broker:** [https://test.mosquitto.org/](https://test.mosquitto.org/)

---

## 7. Important Notes

- **Team Size:** 5–6 students per team (existing groups).
- **Pin Remapping:** Since the original kit uses an Arduino PLUS board, you must remap all pin connections to the ESP32. Pay special attention to analog pins (the ESP32 uses different ADC channels) and PWM-capable pins. Document your full pin mapping in the README and portfolio.
- **MQ-2 Gas Sensor Safety:** The MQ-2 sensor requires a warm-up period of 1–2 minutes before readings are accurate. Do not expose the sensor to high concentrations of flammable gas. Use only small, controlled amounts for testing (e.g., lighter gas at a distance).
- **Submission:** All deliverables (code, portfolio, presentation slides) must be submitted via the LMS. Check the LMS for submission dates and detailed instructions.
- **Academic Integrity:** All work must be original. Code copied from external sources must be attributed. Plagiarism in the portfolio will result in disciplinary action.
- **Late Submissions:** Refer to the LMS for the late submission policy.
- **Hardware Care:** Handle the kit components with care. You are responsible for the condition of the kit and the assembled smart home structure.

---

*EPG317E — Engineering Programming III | Central University of Technology, Free State*
