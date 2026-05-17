import panel as pn
import paho.mqtt.client as mqtt
import pandas as pd
import hvplot.pandas
import datetime
import threading

import database as db  # ← all DB work lives here now

# Initialize Panel Extensions
pn.extension("echarts", "tabulator")

# --- CSS OVERRIDE ---
pn.config.raw_css.append("""
    .bk-root { color: #00FFFF !important; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #00FFFF !important; }
    .bk-panel-models-widgets-StaticText { color: #00FFFF; }
    .tabulator { background-color: #1c1c1e !important; }
""")

# --- CONFIG ---
MQTT_BROKER = "broker.hivemq.com"
USER_PREFIX = "kamo"

# Initialise DB tables on startup
db.init_db()

# --- STATE MANAGEMENT ---
state = {
    "door": "CLOSED",
    "window": "CLOSED",
    "fan": "OFF",
    "relay": "ON",
    "security": "DISARMED",
    "light": 0,
    "rain": 0,
    "gas": 0,
    "motion": "OFF",
}

# --- UI COMPONENTS ---
clock = pn.widgets.StaticText(
    value="", styles={"font-size": "32pt", "font-weight": "bold", "color": "#00ff88"}
)
date_text = pn.widgets.StaticText(
    value="", styles={"font-size": "16pt", "color": "#00FFFF"}
)
day_night = pn.widgets.StaticText(
    value="☀️ DAY", styles={"font-size": "18pt", "font-weight": "bold"}
)
online_ind = pn.indicators.BooleanStatus(
    value=False, color="success", width=30, height=30
)


def update_time():
    now = datetime.datetime.now()
    clock.value = now.strftime("%H:%M:%S")
    date_text.value = now.strftime("%A, %d %B %Y")
    is_night = state["light"] < 500
    day_night.value = "🌙 NIGHT" if is_night else "☀️ DAY"
    day_night.styles = {"color": "#3a86ff" if is_night else "#ffbe0b"}


pn.state.add_periodic_callback(update_time, 1000)


# --- SENSOR BLOCKS ---
def create_sensor_block(name, key, unit=""):
    val_text = pn.widgets.StaticText(
        value=f"{state[key]} {unit}", styles={"font-size": "22pt", "color": "white"}
    )

    def update():
        val_text.value = f"{state[key]} {unit}"

    pn.state.add_periodic_callback(update, 500)
    return pn.Column(
        pn.pane.Markdown(f"### {name.upper()}"),
        val_text,
        styles={
            "background": "#2a2a2e",
            "padding": "15px",
            "border-left": "5px solid #00FFFF",
            "border-radius": "10px",
        },
        width=160,
    )


gas_blk = create_sensor_block("Gas", "gas", "ppm")
rain_blk = create_sensor_block("Rain", "rain")
light_blk = create_sensor_block("Light", "light")
motion_blk = create_sensor_block("Motion", "motion")

weather_val = pn.widgets.StaticText(
    name="Current Weather",
    value="Sunny ☀️",
    styles={"font-size": "16pt", "color": "#00FFFF"},
)
door_cnt = pn.indicators.Number(name="Door Opens", value=0, font_size="22pt")
win_cnt = pn.indicators.Number(name="Window Opens", value=0, font_size="22pt")

# --- EVENT STREAM TABLE ---
_empty_log = pd.DataFrame(
    {
        "Time": pd.Series(dtype="str"),
        "GAS": pd.Series(dtype="float"),
        "RAIN": pd.Series(dtype="float"),
        "LIGHT": pd.Series(dtype="float"),
        "MOTION": pd.Series(dtype="str"),
        "FAN": pd.Series(dtype="str"),
        "DOOR": pd.Series(dtype="str"),
        "RELAY": pd.Series(dtype="str"),
        "SEC": pd.Series(dtype="str"),
    }
)

log_table = pn.widgets.Tabulator(
    _empty_log,
    theme="midnight",
    height=400,
    sizing_mode="stretch_width",
    pagination="remote",
    page_size=10,
)

# --- ANALYTICS ---
analytics_container = pn.Column(
    pn.pane.Alert("### 📊 Waiting for sensor data...", alert_type="info"),
    sizing_mode="stretch_width",
)


def refresh_analytics():
    try:
        df = db.get_telemetry(limit=500)

        if df.empty:
            analytics_container.objects = [
                pn.pane.Alert("### 📊 Waiting for sensor data...", alert_type="info")
            ]
            return

        plots = []

        env_df = df[df["sensor"].isin(["gas", "light", "rain"])]
        if not env_df.empty:
            env_chart = env_df.hvplot.line(
                x="timestamp",
                y="value",
                by="sensor",
                height=250,
                responsive=True,
                title="Environment Metrics",
                color=["#00FFFF", "#00ff88", "#ffbe0b"],
                grid=True,
            )
            plots.append(pn.pane.HoloViews(env_chart, sizing_mode="stretch_width"))

        state_df = df[df["sensor"].isin(["door", "window", "fan", "relay"])]
        if not state_df.empty:
            state_chart = state_df.hvplot.step(
                x="timestamp",
                y="value",
                by="sensor",
                height=250,
                responsive=True,
                title="Logic States  (1 = ON/OPEN,  0 = OFF/CLOSED)",
                grid=True,
            )
            plots.append(pn.pane.HoloViews(state_chart, sizing_mode="stretch_width"))

        analytics_container.objects = (
            plots
            if plots
            else [pn.pane.Alert("### 📊 Not enough data yet...", alert_type="warning")]
        )

    except Exception as e:
        analytics_container.objects = [
            pn.pane.Alert(f"### ⚠️ Chart error: {e}", alert_type="danger")
        ]


pn.state.add_periodic_callback(refresh_analytics, 5000)

try:
    removed = db.purge_old_records(days=7)
    if removed:
        print(f"Purged {removed} old DB records.")
except Exception as e:
    print(f"Purge warning: {e}")


# --- MQTT CALLBACK ---
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8").strip()
        topic = msg.topic
        sensor_id = topic.split("/")[-1]

        if "gas" in topic:
            state["gas"] = float(payload)
        elif "light" in topic:
            state["light"] = float(payload)
        elif "rain" in topic:
            state["rain"] = float(payload)
        elif "motion" in topic:
            state["motion"] = payload
        elif "status/door" in topic:
            state["door"] = payload
        elif "status/window" in topic:
            state["window"] = payload
        elif "status/fan" in topic:
            state["fan"] = payload
        elif "status/relay" in topic:
            state["relay"] = payload
        elif "status/armed" in topic:
            state["security"] = payload
        elif "door/count" in topic:
            door_cnt.param.update(value=int(payload))
        elif "window/count" in topic:
            win_cnt.param.update(value=int(payload))

        if state["rain"] > 1000:
            weather_val.value = "Raining 🌧️"
        elif state["light"] > 1500:
            weather_val.value = "Sunny ☀️"
        else:
            weather_val.value = "Cloudy ☁️"

        def _update_widgets():
            online_ind.value = True
            log_table.stream(
                {
                    "Time": [datetime.datetime.now().strftime("%H:%M:%S")],
                    "GAS": [float(state["gas"])],
                    "RAIN": [float(state["rain"])],
                    "LIGHT": [float(state["light"])],
                    "MOTION": [str(state["motion"])],
                    "FAN": [str(state["fan"])],
                    "DOOR": [str(state["door"])],
                    "RELAY": [str(state["relay"])],
                    "SEC": [str(state["security"])],
                },
                follow=True,
                rollover=200,
            )

        if pn.state.curdoc is not None:
            pn.state.curdoc.add_next_tick_callback(_update_widgets)
        else:
            _update_widgets()

        numeric_val = None
        if payload in ["OPEN", "ON", "ARMED"]:
            numeric_val = 1.0
        elif payload in ["CLOSED", "OFF", "DISARMED"]:
            numeric_val = 0.0
        else:
            try:
                numeric_val = float(payload)
            except:
                pass

        if numeric_val is not None:
            db.insert_telemetry(sensor_id, numeric_val)

        db.insert_event(state)

    except Exception as e:
        print(f"MQTT Error: {e}")


# --- START MQTT ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = on_message
try:
    mqtt_client.connect(MQTT_BROKER, 1883, keepalive=60)
    mqtt_client.subscribe(f"{USER_PREFIX}/home/#")
    mqtt_client.loop_start()
    print("MQTT connected and subscribed.")
except Exception as e:
    print(f"MQTT connection failed: {e}")


# --- BUTTONS & CONTROLS ---
def send(sub, m):
    mqtt_client.publish(f"{USER_PREFIX}/home/{sub}", m)


def create_btn(name, key, sub_path, on_v, off_v, on_c="success", off_c="danger"):
    btn = pn.widgets.Button(
        name=f"{name}: {state[key]}", height=55, sizing_mode="stretch_width"
    )

    def toggle(e):
        target = off_v if state[key] == on_v else on_v
        send(sub_path, target)

    btn.on_click(toggle)

    def update():
        btn.name = f"{name}: {state[key]}"
        btn.button_type = on_c if state[key] == on_v else off_c

    pn.state.add_periodic_callback(update, 500)
    return btn


# --- LAYOUT ---
header = pn.Row(
    pn.Column(clock, date_text, width=450),
    pn.Spacer(),
    pn.Column(
        day_night,
        pn.Row(pn.widgets.StaticText(value="SYSTEM ONLINE:"), online_ind),
        align="center",
    ),
    styles={
        "background": "#1c1c1e",
        "padding": "20px",
        "border-bottom": "4px solid #00FFFF",
    },
    sizing_mode="stretch_width",
)

controls = pn.Column(
    "## Controls",
    create_btn("DOOR", "door", "door/control", "OPEN", "CLOSED"),
    create_btn("WINDOW", "window", "window/control", "OPEN", "CLOSED"),
    create_btn("FAN", "fan", "fan/control", "ON", "OFF"),
    create_btn("RELAY", "relay", "relay/control", "ON", "OFF"),
    create_btn(
        "SECURITY",
        "security",
        "control/arm",
        "ARMED",
        "DISARMED",
        on_c="warning",
        off_c="primary",
    ),
    width=350,
)

dashboard = pn.Column(
    header,
    pn.Row(
        pn.Column(
            "## Live Metrics",
            pn.Row(gas_blk, rain_blk, light_blk, motion_blk),
            pn.Row(
                weather_val,
                door_cnt,
                win_cnt,
                styles={
                    "margin-top": "20px",
                    "background": "#212121",
                    "padding": "10px",
                    "border-radius": "10px",
                },
            ),
            sizing_mode="stretch_width",
        ),
        controls,
        margin=(20, 20),
    ),
    pn.Tabs(
        ("Event Stream", log_table),
        ("Analytics", analytics_container),
    ),
    sizing_mode="stretch_width",
)

dashboard.servable()
