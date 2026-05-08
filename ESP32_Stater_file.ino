#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>
#include "OneButton.h"


//PINS
#define LED_outside 13
#define LED_inside 12
#define photocell_sensor 33
#define steam_sensor 25
#define gas_sensor 26
#define pir_sensor 27
#define window_servo_pin 18
#define door_servo_pin 15
#define btn1 17
#define btn2 16
#define relay_pin 14
#define buzzer_pin 19
#define fanPin1 32
#define fanPin2 23

// PWM properties for LED
const int freq = 5000;
const int resolution = 8;

// Servo positions
#define WINDOW_OPEN 0
#define WINDOW_CLOSED 176
#define DOOR_OPEN 0
#define DOOR_CLOSED 180

LiquidCrystal_I2C mylcd(0x27,16,2);
Servo windowServo;
Servo doorServo;
OneButton button1(btn1, true); 
OneButton button2(btn2, true);
//BuzzerESP32 buzzer(buzzer_pin);

int led_brightness = 135;
int light_intensity = 0;
int steam_sensor_val = 0;
int gas_level = 0;
bool windowOpen = false;
bool doorOpen = false;
bool relay_state = false;
bool fan_is_on = false;
bool LED_outside_on = false;
bool alarm_status = false;


void setup() {
  Serial.begin(115200);
  
  pinMode(buzzer_pin, OUTPUT);
  pinMode(LED_outside, OUTPUT);

  // Configure LEDC for inside LED brightness control
  ledcAttach(LED_inside, freq, resolution);
  ledcWrite(LED_inside, led_brightness);

  pinMode(relay_pin, OUTPUT);
  digitalWrite(relay_pin, LOW);

  pinMode(pir_sensor, INPUT);

  // Setup fan pins using pinMode
  pinMode(fanPin1, OUTPUT);
  pinMode(fanPin2, OUTPUT);

  // Add these lines for servo setup
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  windowServo.setPeriodHertz(50);    // standard 50 hz servo
  windowServo.attach(window_servo_pin, 1000, 2000);
  windowServo.write(WINDOW_CLOSED); // close the window

  doorServo.setPeriodHertz(50);      // standard 50 hz servo
  doorServo.attach(door_servo_pin, 1000, 2000);
  doorServo.write(DOOR_CLOSED); // close the door
  
  mylcd.init();
  mylcd.backlight();

  button1.attachClick(click1);
  button1.attachLongPressStart(longPressClick1);

  button2.attachClick(click2);
  button2.attachLongPressStart(longPressClick2);

  mylcd.setCursor(0, 0);
  mylcd.print("hello");
  mylcd.setCursor(0, 1);
  mylcd.print("keyestudio");                                
}

// the loop function runs over and over again forever
void loop() {

  button1.tick();
  button2.tick();

  light_intensity = analogRead(photocell_sensor);
  steam_sensor_val = analogRead(steam_sensor);
  gas_level = analogRead(gas_sensor);

  if(digitalRead(pir_sensor) == HIGH){
    digitalWrite(LED_outside, HIGH);
    LED_outside_on = true;
  }
  else{
    digitalWrite(LED_outside, LOW);
    LED_outside_on = false;
  }

  char incomingChar = Serial.read();
  if (incomingChar == 'w') {
    windowServo.write(windowOpen ? WINDOW_CLOSED : WINDOW_OPEN);
    windowOpen = !windowOpen;
  }
  if (incomingChar == 'a'){
    if(alarm_status){
      digitalWrite(buzzer_pin, LOW);
      alarm_status = !alarm_status;
    }
    else{
      digitalWrite(buzzer_pin, HIGH);
      alarm_status = !alarm_status;
    }
  }
  if (incomingChar == 'd') {
   doorServo.write(doorOpen ? DOOR_CLOSED : DOOR_OPEN);
   doorOpen = !doorOpen;
  }
  if (incomingChar == 'r') {
   digitalWrite(relay_pin, relay_state ? LOW : HIGH);
   relay_state = !relay_state;
  }

  if (incomingChar == 'b') {
    if(led_brightness < 255){
      led_brightness += 15;
      ledcWrite(LED_inside, led_brightness);
    }
  } 
  else if (incomingChar == 'n') {
    if(led_brightness > 0){
      led_brightness -= 15;
      ledcWrite(LED_inside, led_brightness);
    }
  }

  if (incomingChar == 'f') {
    if (fan_is_on){
      // Turn OFF
      analogWrite(fanPin1, 0);
      analogWrite(fanPin2, 0);
      fan_is_on = false;
    }
    else {
      // Turn ON
      digitalWrite(fanPin1, HIGH);
      analogWrite(fanPin2, 210);
      fan_is_on = true;
    }
  }

  Serial.print("Light Intensity: ");
  Serial.println(light_intensity);
  Serial.print("Steam Sensor: ");
  Serial.println(steam_sensor_val);
  Serial.print("Gas Level: ");
  Serial.println(gas_level);
  Serial.print("Led Brightness: ");
  Serial.println(led_brightness);
  Serial.print("Fan Started: ");
  Serial.println(fan_is_on); 
  Serial.print("Door Open: ");
  Serial.println(doorOpen); 
  Serial.print("Window Open: ");
  Serial.println(windowOpen); 
  Serial.print("Outside LED on: ");
  Serial.println(LED_outside_on); 

  delay(100);
}


void click1() {
  windowServo.write(windowOpen ? WINDOW_CLOSED : WINDOW_OPEN);
  windowOpen = !windowOpen;
}

void longPressClick1(){
  if (fan_is_on){
    // Turn OFF
    analogWrite(fanPin1, 0);
    analogWrite(fanPin2, 0);
    fan_is_on = false;
  }
  else {
    // Turn ON
    digitalWrite(fanPin1, HIGH);
    analogWrite(fanPin2, 210);
    fan_is_on = true;
  }
}

void click2() {
  doorServo.write(doorOpen ? DOOR_CLOSED : DOOR_OPEN);
  doorOpen = !doorOpen;
} 

void longPressClick2(){
  digitalWrite(relay_pin, relay_state ? LOW : HIGH);
  relay_state = !relay_state;
}
