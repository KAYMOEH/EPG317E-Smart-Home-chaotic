"""
subscribe_mqtt.py

This script subscribes to MQTT messages from the ESP32 smart home system,
processes incoming JSON sensor data, and stores it into a SQLite database.

Author: Memory Moyo
Project: EPG317E IoT Smart Home
"""

import json
import sqlite3
from datetime import datetime

import paho.mqtt.client as mqtt

# ==============================
# MQTT CONFIGURATION
# ==============================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "cut/smarthome/kamo/sensors"

# ==============================
# DATABASE CONFIGURATION
# ==============================
DB_FILE = "smart_home.db"


def insert_sensor_data(sensor_type: str, value):
    """
    Insert a single sensor reading into the database.

    Args:
        sensor_type (str): Type of sensor (light, gas, steam, motion)
        value (float/int): Sensor value
    """
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO sensor_data (timestamp, sensor_type, value)
        VALUES (?, ?, ?)
        """, (timestamp, sensor_type, value))

        connection.commit()
        connection.close()

        print(f"💾 Saved: {sensor_type} = {value}")

    except Exception as error:
        print(f"❌ Database error: {error}")


def on_connect(client, userdata, flags, rc):
    """
    Callback when MQTT client connects to the broker.
    """
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"❌ Connection failed with code {rc}")


def on_message(client, userdata, msg):
    """
    Callback when a message is received from MQTT.

    Processes JSON data and stores each sensor value.
    """
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        print(f"📥 Received data: {data}")

        # Extract and store each sensor value
        insert_sensor_data("light", data.get("light"))
        insert_sensor_data("gas", data.get("gas"))
        insert_sensor_data("steam", data.get("steam"))
        insert_sensor_data("motion", data.get("motion"))

    except json.JSONDecodeError:
        print("❌ Failed to decode JSON data")

    except Exception as error:
        print(f"❌ Error processing message: {error}")


def main():
    """
    Main function to start MQTT subscriber.
    """
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    print("🔌 Connecting to MQTT broker...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    print("🚀 Listening for sensor data...")
    client.loop_forever()


if __name__ == "__main__":
    main()