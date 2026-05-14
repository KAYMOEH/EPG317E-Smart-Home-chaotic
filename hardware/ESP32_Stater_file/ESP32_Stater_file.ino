#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>
#include "OneButton.h"

// =====================================================
//                  WIFI & MQTT
// =====================================================
const char* ssid = "Galaxy S22+";
const char* password = "qwertyuio";
const char* mqtt_server = "broker.hivemq.com";

// =====================================================
//                  PIN MAPPING
// =====================================================
#define LED_outside 13
#define LED_inside 12
#define photocell_sensor 33
#define steam_sensor 35
#define gas_sensor 34
#define pir_sensor 27
#define window_servo_pin 18
#define door_servo_pin 15
#define btn1 17
#define btn2 16
#define relay_pin 14
#define buzzer_pin 19
#define fanPin1 32
#define fanPin2 23

// =====================================================
//                  THRESHOLDS
// =====================================================
const int gasThreshold = 1000;
const int rainThreshold = 1000;
const int lightThreshold = 1500;

// =====================================================
//                  SERVO POSITIONS
// =====================================================
#define WINDOW_OPEN 176
#define WINDOW_CLOSED 0
#define DOOR_OPEN 0
#define DOOR_CLOSED 180

// =====================================================
//                  OBJECTS
// =====================================================
LiquidCrystal_I2C mylcd(0x27, 16, 2);

Servo windowServo;
Servo doorServo;

OneButton button1(btn1, true);
OneButton button2(btn2, true);

WiFiClient espClient;
PubSubClient client(espClient);

// =====================================================
//                  GLOBAL VARIABLES
// =====================================================
bool windowOpen = false;
bool doorOpen = false;
bool fan_is_on = false;
bool relay_state = true;
bool systemArmed = true;

int doorCount = 0;
int windowCount = 0;

unsigned long lastReconnectAttempt = 0;
unsigned long lastWifiAttempt = 0;
unsigned long lastMsg = 0;
unsigned long lastDebug = 0;
unsigned long lastBuzzerMillis = 0;

bool buzzerToggle = false;

// =====================================================
//                  WIFI SETUP
// =====================================================
void setup_wifi() {

  if (WiFi.status() == WL_CONNECTED) return;

  if (millis() - lastWifiAttempt > 10000) {

    Serial.println("Connecting to WiFi...");

    WiFi.begin(ssid, password);

    lastWifiAttempt = millis();
  }
}

// =====================================================
//                  MQTT CALLBACK
// =====================================================
void callback(char* topic, byte* payload, unsigned int length) {

  String msg = "";

  for (int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }

  Serial.print("Message [");
  Serial.print(topic);
  Serial.print("] : ");
  Serial.println(msg);

  // =================================================
  //                  DOOR CONTROL
  // =================================================
  if (String(topic) == "kamo/home/door/control") {

    if (msg == "OPEN") {

      doorServo.write(DOOR_OPEN);
      doorOpen = true;
      doorCount++;
    }

    else if (msg == "CLOSE" || msg == "CLOSED") {

      doorServo.write(DOOR_CLOSED);
      doorOpen = false;
    }
  }

  // =================================================
  //                  WINDOW CONTROL
  // =================================================
  if (String(topic) == "kamo/home/window/control") {

    if (msg == "OPEN") {

      windowServo.write(WINDOW_OPEN);
      windowOpen = true;
      windowCount++;
    }

    else if (msg == "CLOSE" || msg == "CLOSED") {

      windowServo.write(WINDOW_CLOSED);
      windowOpen = false;
    }
  }

  // =================================================
  //                  FAN CONTROL
  // =================================================
  if (String(topic) == "kamo/home/fan/control") {

    fan_is_on = (msg == "ON");
  }

  // =================================================
  //                  ARM SYSTEM
  // =================================================
  if (String(topic) == "kamo/home/control/arm") {

    systemArmed = (msg == "ARMED");
  }

  // =================================================
  //                  RELAY CONTROL
  // =================================================
  if (String(topic) == "kamo/home/relay/control") {

    if (msg == "ON") {

      relay_state = true;
      digitalWrite(relay_pin, HIGH);
    }

    else if (msg == "OFF") {

      relay_state = false;
      digitalWrite(relay_pin, LOW);
    }
  }
}

// =====================================================
//                  MQTT RECONNECT
// =====================================================
boolean reconnect() {

  Serial.println("Attempting MQTT connection...");

  if (client.connect("ESP32_SmartHome_Kamo")) {

    Serial.println("MQTT Connected");

    client.subscribe("kamo/home/door/control");
    client.subscribe("kamo/home/window/control");
    client.subscribe("kamo/home/fan/control");
    client.subscribe("kamo/home/control/arm");
    client.subscribe("kamo/home/relay/control");
  }

  return client.connected();
}

// =====================================================
//                  BUTTON FUNCTIONS
// =====================================================
void click1() {

  windowServo.write(windowOpen ? WINDOW_CLOSED : WINDOW_OPEN);

  windowOpen = !windowOpen;

  if (windowOpen) {
    windowCount++;
  }
}

void longPressClick1() {

  fan_is_on = !fan_is_on;
}

void click2() {

  doorServo.write(doorOpen ? DOOR_CLOSED : DOOR_OPEN);

  doorOpen = !doorOpen;

  if (doorOpen) {
    doorCount++;
  }
}

void longPressClick2() {

  relay_state = !relay_state;

  digitalWrite(relay_pin, relay_state ? HIGH : LOW);
}

// =====================================================
//                      SETUP
// =====================================================
void setup() {

  Serial.begin(115200);

  WiFi.setSleep(false);

  setup_wifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  pinMode(LED_outside, OUTPUT);
  pinMode(LED_inside, OUTPUT);
  pinMode(pir_sensor, INPUT);

  pinMode(relay_pin, OUTPUT);

  pinMode(fanPin1, OUTPUT);
  pinMode(fanPin2, OUTPUT);

  pinMode(buzzer_pin, OUTPUT);

  pinMode(btn1, INPUT_PULLUP);
  pinMode(btn2, INPUT_PULLUP);

  digitalWrite(relay_pin, HIGH);

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  windowServo.setPeriodHertz(50);
  windowServo.attach(window_servo_pin, 1000, 2000);
  windowServo.write(WINDOW_CLOSED);

  delay(500);

  doorServo.setPeriodHertz(50);
  doorServo.attach(door_servo_pin, 1000, 2000);
  doorServo.write(DOOR_CLOSED);

  delay(500);

  mylcd.init();
  mylcd.backlight();

  mylcd.setCursor(0, 0);
  mylcd.print("SMART HOME");

  mylcd.setCursor(0, 1);
  mylcd.print("INITIALIZING");

  button1.attachClick(click1);
  button1.attachLongPressStart(longPressClick1);

  button2.attachClick(click2);
  button2.attachLongPressStart(longPressClick2);

  delay(2000);

  mylcd.clear();
}

// =====================================================
//                        LOOP
// =====================================================
void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }

  if (WiFi.status() == WL_CONNECTED) {

    if (!client.connected()) {

      if (millis() - lastReconnectAttempt > 5000) {

        lastReconnectAttempt = millis();

        reconnect();
      }
    }

    else {

      client.loop();
    }
  }

  button1.tick();
  button2.tick();

  int gasVal = analogRead(gas_sensor);
  int lightVal = analogRead(photocell_sensor);
  int rainVal = analogRead(steam_sensor);

  bool motionDetected = digitalRead(pir_sensor);

  // =================================================
  //                  GAS ALERT
  // =================================================
  if (gasVal > gasThreshold) {

    if (millis() - lastBuzzerMillis > 150) {

      lastBuzzerMillis = millis();

      buzzerToggle = !buzzerToggle;

      analogWrite(buzzer_pin, buzzerToggle ? 80 : 0);
    }

    digitalWrite(fanPin1, HIGH);
    analogWrite(fanPin2, 150);

    windowServo.write(WINDOW_OPEN);
    windowOpen = true;

    digitalWrite(relay_pin, LOW);

    mylcd.setCursor(0, 0);
    mylcd.print("GAS LEAK ALERT");

    mylcd.setCursor(0, 1);
    mylcd.print("WINDOW OPEN   ");
  }

  else {

    analogWrite(buzzer_pin, 0);

    if (fan_is_on) {

      digitalWrite(fanPin1, HIGH);
      analogWrite(fanPin2, 150);
    }

    else {

      digitalWrite(fanPin1, LOW);
      analogWrite(fanPin2, 0);
    }

    digitalWrite(relay_pin, relay_state ? HIGH : LOW);

    if (rainVal > rainThreshold) {

      windowServo.write(WINDOW_CLOSED);

      windowOpen = false;

      mylcd.setCursor(0, 0);
      mylcd.print("RAIN DETECTED ");

      mylcd.setCursor(0, 1);
      mylcd.print("WINDOW CLOSED ");
    }

    else if (motionDetected && systemArmed) {

      digitalWrite(LED_inside, HIGH);

      analogWrite(buzzer_pin, 50);

      mylcd.setCursor(0, 0);
      mylcd.print("MOTION ALERT  ");

      mylcd.setCursor(0, 1);
      mylcd.print("INSIDE HOUSE  ");

      doorServo.write(DOOR_CLOSED);

      doorOpen = false;
    }

    else {

      digitalWrite(LED_inside, LOW);

      analogWrite(buzzer_pin, 0);

      mylcd.setCursor(0, 0);
      mylcd.print("SYSTEM NORMAL ");

      mylcd.setCursor(0, 1);
      mylcd.print("ALL SAFE      ");
    }

    digitalWrite(LED_outside, (lightVal < lightThreshold));
  }

  // =================================================
  //                  MQTT PUBLISH
  // =================================================
  if (client.connected() && millis() - lastMsg > 5000) {

    lastMsg = millis();

    client.publish("kamo/home/sensors/gas", String(gasVal).c_str());
    client.publish("kamo/home/sensors/rain", String(rainVal).c_str());
    client.publish("kamo/home/sensors/light", String(lightVal).c_str());

    client.publish(
      "kamo/home/sensors/motion",
      motionDetected ? "DETECTED" : "OFF"
    );

    client.publish("kamo/home/door/count", String(doorCount).c_str());
    client.publish("kamo/home/window/count", String(windowCount).c_str());

    client.publish(
      "kamo/home/status/door",
      doorOpen ? "OPEN" : "CLOSED"
    );

    client.publish(
      "kamo/home/status/window",
      windowOpen ? "OPEN" : "CLOSED"
    );

    client.publish(
      "kamo/home/status/fan",
      fan_is_on ? "ON" : "OFF"
    );

    client.publish(
      "kamo/home/status/relay",
      relay_state ? "ON" : "OFF"
    );

    client.publish(
      "kamo/home/status/armed",
      systemArmed ? "ARMED" : "DISARMED"
    );
  }

  // =================================================
  //                  DEBUG SERIAL
  // =================================================
  if (millis() - lastDebug > 1000) {

    lastDebug = millis();

    Serial.print("WiFi:");
    Serial.print(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");

    Serial.print(" | MQTT:");
    Serial.print(client.connected() ? "Connected" : "Disconnected");

    Serial.print(" | GAS:");
    Serial.print(gasVal);

    Serial.print(" | RAIN:");
    Serial.print(rainVal);

    Serial.print(" | LIGHT:");
    Serial.print(lightVal);

    Serial.print(" | MOTION:");
    Serial.print(motionDetected);

    Serial.print(" | FAN:");
    Serial.print(fan_is_on ? "ON" : "OFF");

    Serial.print(" | DOOR:");
    Serial.print(doorOpen ? "OPEN" : "CLOSED");

    Serial.print(" | WINDOW:");
    Serial.print(windowOpen ? "OPEN" : "CLOSED");

    Serial.print(" | RELAY:");
    Serial.print(relay_state ? "ON" : "OFF");

    Serial.print(" | DoorCnt:");
    Serial.print(doorCount);

    Serial.print(" | WinCnt:");
    Serial.println(windowCount);
  }
}