#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include <Wire.h>

const char* WIFI_SSID="YOUR_WIFI_NAME";
const char* WIFI_PASS="YOUR_WIFI_PASSWORD";
const int PAN_STEP=2, PAN_DIR=3, PAN_EN=8, TILT_SERVO=9;
// Verify the SDA/SCL labels on your exact Nano ESP32 before wiring.
const int SDA_PIN=A4, SCL_PIN=A5;
WebServer server(80); Servo tiltServo;
long panPosition=0; int tiltAngle=90, panDir=1, panSpeed=180, tiltSpeed=35;
bool enabled=false, estopped=false; unsigned long lastCmd=0,lastStep=0;
void stepPan(){if(!enabled||estopped)return; unsigned long iv=1000000UL/max(1,panSpeed); if(micros()-lastStep>=iv){lastStep=micros();digitalWrite(PAN_STEP,HIGH);delayMicroseconds(3);digitalWrite(PAN_STEP,LOW);panPosition+=panDir;}}
void stopM(){enabled=false;digitalWrite(PAN_EN,HIGH);}
void command(){String b=server.arg("plain");lastCmd=millis();if(b.indexOf("\"cmd\":\"estop\"")>=0){estopped=true;stopM();}else if(b.indexOf("\"cmd\":\"stop\"")>=0)stopM();else if(b.indexOf("\"cmd\":\"left\"")>=0){estopped=false;enabled=true;panDir=-1;digitalWrite(PAN_EN,LOW);}else if(b.indexOf("\"cmd\":\"right\"")>=0){estopped=false;enabled=true;panDir=1;digitalWrite(PAN_EN,LOW);}else if(b.indexOf("\"cmd\":\"up\"")>=0){tiltAngle=min(170,tiltAngle+max(1,tiltSpeed/5));tiltServo.write(tiltAngle);}else if(b.indexOf("\"cmd\":\"down\"")>=0){tiltAngle=max(10,tiltAngle-max(1,tiltSpeed/5));tiltServo.write(tiltAngle);}server.send(200,"application/json","{\"ok\":true}");}
void status(){server.send(200,"application/json","{\"pan\":"+String(panPosition)+",\"tilt\":"+String(tiltAngle)+"}");}
void setup(){Serial.begin(115200);pinMode(PAN_STEP,OUTPUT);pinMode(PAN_DIR,OUTPUT);pinMode(PAN_EN,OUTPUT);digitalWrite(PAN_EN,HIGH);tiltServo.setPeriodHertz(50);tiltServo.attach(TILT_SERVO,500,2500);tiltServo.write(90);Wire.begin(SDA_PIN,SCL_PIN);WiFi.begin(WIFI_SSID,WIFI_PASS);while(WiFi.status()!=WL_CONNECTED){delay(400);Serial.print(".");}Serial.println(WiFi.localIP());server.on("/api/command",HTTP_POST,command);server.on("/api/status",HTTP_GET,status);server.begin();}
void loop(){server.handleClient();if(enabled&&millis()-lastCmd>2000)stopM();stepPan();}
