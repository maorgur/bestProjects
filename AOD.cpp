#include <Arduino.h>

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#define SEALEVELPRESSURE_HPA (1013.25)
#include <ESP8266WiFi.h>
#include <time.h>
#include <string>

#include <ScreenManager.hpp>
#include <ExternalData.hpp>
#include "config.h"

#include <LEDManager.hpp>

#define BAUD_RATE 2000000


const char* ssid = WIFI_SSID;
const char* pass = WIFI_PASS;

const char* tz = TIMEZONE; //means il, and take DST into account

const int timePerScreen = 10000; //10s
const int updateTime = 250; //250ms
const int backlightOffTimout = 10000; //10s

Adafruit_BME280 bme; // I2C
Screen lcd = Screen(); 

char current_time[30];
time_t now;

void setup() {
  //serial
  Serial.begin(BAUD_RATE);
  Serial.setTimeout(50); //required by LED manager
  
  //LED strip
  LEDSetup();

  //screen
  lcd.init();
  
  //bme
  bme.begin(0x76);

  lcd.printToScreenf(0, true, "connecting to %s...", ssid);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) delay(500); //wait until connected

  String testText = getTest();
  while (testText.length() != 0){
    lcd.printToScreen(testText.c_str(), 0, true);
    delay(2000);
    testText = getTest();
  }
  lcd.printToScreen("connected, getting time...", 0, true);


  configTime(tz, "pool.ntp.org", "time.nist.gov");
  while ((now = time(nullptr)) < 100000) delay(500); // wait for sync

  struct tm* t = localtime(&now);
  Serial.println("got time:");
  Serial.printf("%04d-%02d-%02d %02d:%02d:%02d\n",
  t->tm_year + 1900, t->tm_mon + 1, t->tm_mday,
  t->tm_hour, t->tm_min, t->tm_sec);

}

double temp, pressure, humidity, feels, waterVaporPressure;
int altitude, light;
bool lightMode = true;
int currentScreen = 0; //0 time, 1 temp, 2 planes, 3 stats, 4 media
int const screenCount = 5; //5 full, 2 shabbat
int timeInScreen = 0;
int timeSinceTurnedOff = -1;

bool activeMedia = false; //will be true if the last check of media returned data, will signal to skip boring screens
bool activePlanes = false; //will be true if the last check of planes returned data, will signal to skip boring screens
char toLCD[100];
void loop() {

  if (currentScreen == 0){ //time

    now = time(nullptr);
    struct tm* t = localtime(&now);
    lcd.printToScreenf(0, false, "%02d:%02d:%02d\n%02d-%02d", t->tm_hour, t->tm_min, t->tm_sec, t->tm_mday, t->tm_mon+1);


  } else if (currentScreen == 1){ //temp
    temp = bme.readTemperature();
    pressure = bme.readPressure() / 100.0;
    humidity = bme.readHumidity();
    altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);
    waterVaporPressure = (humidity/100)*6.105*exp((17.27*temp)/(237.7+temp)); 
    feels = temp + 0.33*waterVaporPressure-4;

    lcd.printToScreenf(0, false, "%.1fC %.1f%%\nFeels %.1fC", temp, humidity, feels);    

  }


  if (timeInScreen >= timePerScreen){ //iterate to the next screen
    currentScreen = (currentScreen + 1) % screenCount;
    timeInScreen = 0;

    if ((activeMedia || activePlanes) && currentScreen <= 1){ //time and temp are boring screens
      currentScreen = 2; //skip to planes
      if (activePlanes){
        timeInScreen = timePerScreen - 2000; //fast updates, every 2s
      }

    }


    //ADD HERE SCREENS THAT SHOULD ONLY BE UPDATED ONCE PER SCREEN
    if (currentScreen == 2){ //planes
    String planeString = getPlanes();
    if (planeString.length() == 0){
      timeInScreen = timePerScreen; //skip
      activePlanes = false;
    } else {
      lcd.printToScreen(planeString.c_str(), 0, false);
      activePlanes = true;
    }

    } else if (currentScreen == 3){ //availability
      String availabilityString = getAvailability();
      if (availabilityString.length() == 0){
        timeInScreen = timePerScreen; //skip
      } else {
        lcd.printToScreen(availabilityString.c_str(), 0, false);
      }
    } else if (currentScreen == 4){ //media
      String mediaString = getMedia();
      if (mediaString.length() == 0){
        timeInScreen = timePerScreen; //skip
        activeMedia = false;
      } else {
        lcd.printToScreen(mediaString.c_str(), 0, false);
        activeMedia = true;
      }
    }
  }


  if (timePerScreen < timeInScreen + updateTime){ //if there is not enough time to do a full wait, do until the screen switch
    delay(timePerScreen - timeInScreen);
    if (timeSinceTurnedOff != -1){timeSinceTurnedOff += timePerScreen - timeInScreen;}
    timeInScreen = timePerScreen;
  
  } else {
    delay(updateTime);
    if (timeSinceTurnedOff != -1){timeSinceTurnedOff += updateTime;}
    timeInScreen += updateTime;
  }

  LEDLoop(lcd);
}
