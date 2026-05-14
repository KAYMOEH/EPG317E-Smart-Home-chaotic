import matplotlib

matplotlib.use("agg")
import matplotlib.subplots  # type: ignore
import matplotlib.pyplot as plt
import panel as pn
import pandas as pd
import paho.mqtt.client as mqtt
from database import engine

pn.extension(design="material")

# --- MQTT Setup ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Dashboard_Controller_Kamo")
mqtt_client.connect("broker.hivemq.com", 1883, keepalive=60)
mqtt_client.loop_start()


def send_command(msg):
    mqtt_client.publish("cut/smarthome/kamo/commands", str(msg))


# --- Widgets ---
ticker = pn.widgets.IntInput(value=0, visible=False)
sensor_selector = pn.widgets.Select(
    name="Select History Chart", options=["gas", "light", "steam", "motion"]
)

#  Missing Slider
slider_light = pn.widgets.IntSlider(
    name="💡 Indoor Light Brightness (Yellow)", start=0, end=255, value=135
)


def handle_slider(event):
    send_command(f"L{event.new}")


slider_light.param.watch(handle_slider, "value")


@pn.depends(ticker.param.value)
def live_indicators(target_value):
    # FAST QUERY: Grabs only the absolute newest reading for live speed
    df = pd.read_sql(
        "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 1", engine
    )

    if df.empty:
        return pn.pane.Alert(
            "🕒 Waiting for data from bridge.py...", alert_type="warning"
        )

    latest = df.iloc[0]

    # Extract Hardware States
    door_is_open = latest.get("door_state", 0) == 1
    win_is_open = latest.get("window_state", 0) == 1

    door_txt = "🚪 OPEN" if door_is_open else "🚪 CLOSED"
    win_txt = "🪟 OPEN" if win_is_open else "🪟 CLOSED"

    # Door/Window Counter Logic
    all_data = pd.read_sql(
        "SELECT door_state, window_state FROM sensor_readings", engine
    )
    door_log = (
        int(all_data["door_state"].sum()) if "door_state" in all_data.columns else 0
    )
    win_log = (
        int(all_data["window_state"].sum()) if "window_state" in all_data.columns else 0
    )

    return pn.Column(
        pn.Row(
            pn.indicators.Number(
                name="Gas Level",
                value=int(latest["gas"]),
                default_color="success" if latest["gas"] < 400 else "danger",
            ),
            pn.indicators.Number(name="Light Intensity", value=int(latest["light"])),
            pn.indicators.Number(name="Door Total Opens", value=door_log),
            pn.indicators.Number(name="Window Total Opens", value=win_log),
        ),
        pn.pane.Markdown(f"""
        ### 🏠 Hardware Status:
        * **Motion:** {'🚨 DETECTED' if latest['motion'] == 1 else '✅ Clear'}
        * **Door:** {door_txt}
        * **Window:** {win_txt}
        * **Last Sync:** {latest["timestamp"].strftime("%H:%M:%S")}
        """),
    )


@pn.depends(ticker.param.value, sensor_selector.param.value)
def historical_plot(target_value, sensor):
    # FULL QUERY: Grabs 100 points for the chart
    df = pd.read_sql(
        "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 100", engine
    )
    if df.empty:
        return pn.pane.Placeholder(min_height=200)

    plot_df = df.iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 4))
    plot_df.plot(
        x="timestamp",
        y=sensor,
        kind="line",
        title=f"{sensor.capitalize()} Sensor History",
        grid=True,
        ax=ax,
    )
    plt.tight_layout()
    plt.close(fig)
    return pn.pane.Matplotlib(fig, sizing_mode="stretch_width")


# --- Control Widgets ---
btn_fan = pn.widgets.Button(name="🌀 Toggle Fan", button_type="primary")
btn_fan.on_click(lambda e: send_command("f"))
btn_door = pn.widgets.Button(name="🚪 Toggle Door", button_type="warning")
btn_door.on_click(lambda e: send_command("d"))
btn_window = pn.widgets.Button(name="🪟 Toggle Window", button_type="success")
btn_window.on_click(lambda e: send_command("w"))
btn_light = pn.widgets.Button(name="💡 Toggle Primary Relay", button_type="danger")
btn_light.on_click(lambda e: send_command("r"))

# 1-SECOND REFRESH for real-time speed
pn.state.add_periodic_callback(lambda: ticker.param.trigger("value"), period=1000)

# --- Layout ---
dashboard = pn.template.FastListTemplate(
    title="Kamo's Smart Home Control Center",
    sidebar=[
        pn.pane.Markdown("### Remote Controls"),
        btn_fan,
        btn_door,
        btn_window,
        btn_light,
        pn.pane.Markdown("---"),
        slider_light,  # Ensure slider is in the sidebar
        pn.pane.Markdown("---"),
        sensor_selector,
    ],
    main=[
        pn.Column(
            pn.Card(live_indicators, title="Live Sensor & Hardware Status"),
            pn.Card(historical_plot, title="Historical Data Analytics"),
        )
    ],
)
dashboard.show()
