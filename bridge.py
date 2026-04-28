import paho.mqtt.client as mqtt
import json
from database import db_session, SmartHomeReading

# Topic must match exactly what is in your ESP32 code!
MQTT_TOPIC = "cut/smarthome/kamo/sensors"
MQTT_BROKER = "broker.hivemq.com"


def on_message(client, userdata, msg):
    try:
        # Decode the JSON from the ESP32
        data = json.loads(msg.payload.decode())
        print(f"📥 Received: {data}")

        # Create a new database entry
        new_entry = SmartHomeReading(
            light=data.get("light"),
            gas=data.get("gas"),
            steam=data.get("steam"),
            motion=data.get("motion"),
        )

        # Save to SQLite
        db_session.add(new_entry)
        db_session.commit()
        print("💾 Saved to database.")

    except Exception as e:
        print(f"❌ Error processing message: {e}")


client = mqtt.Client()
client.on_message = on_message

print(f"Connecting to {MQTT_BROKER}...")
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC)

print("🚀 Bridge is active. Waiting for data...")
client.loop_forever()
