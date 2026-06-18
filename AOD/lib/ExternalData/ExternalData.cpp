#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Alert.hpp>
#include "../../config.h"
#define DEBUG 0

const char* aircraftURL = EXTERNAL_AIRCRAFT_URL;

String getPlanes(int currentHour) {
  HTTPClient http;
  WiFiClient client;
  http.begin(client, aircraftURL); // HTTP only, not HTTPS!
  int httpCode = http.GET();

  if (httpCode > 0) { // Check for the returning code
    if (httpCode == 200){
      String payload = http.getString();
      int lastNewline = payload.lastIndexOf('\n');
      if (lastNewline > 0) {
        String lastRow = payload.substring(lastNewline + 1);
        payload = payload.substring(0, lastNewline);
        smartAircraftAlert(currentHour, lastRow.c_str());
      }
      http.end();
      return payload;
    } else if (httpCode == 404) {
      http.end();
      return ""; //will signal to skip this screen
    } else {
      http.end();
      if (DEBUG) Serial.printf("HTTP request returned code %d\n", httpCode);
      char errorMsg[32];
      snprintf(errorMsg, sizeof(errorMsg), "HTTP error: %d", httpCode);
      return String(errorMsg);
    }

  } else {
    http.end();
    // Throw an error or handle it as you wish
    if (DEBUG) Serial.printf("HTTP request failed, error: %s\n", http.errorToString(httpCode).c_str());
    // You can throw or return an empty string or error code
    return "Failed to fetch planes :(";
  }
}

const char* availabilityURL = EXTERNAL_AVAILABILITY_URL;
const char* onlineURL = "http://example.com";

String getAvailability() {
  HTTPClient http;
  WiFiClient client;
  http.begin(client, availabilityURL); // HTTP only, not HTTPS!
  int httpCode = http.GET();

  if (httpCode > 0) { // Check for the returning code
    if (httpCode == 200){ //if nothing bad happened, no reason to show this screen
      http.end();
      return String();
    }
    String payload = http.getString();
    http.end();
    return payload;

  } else {
    http.end();
    // Throw an error or handle it as you wish
    if (DEBUG) Serial.printf("HTTP request failed, error: %s\n", http.errorToString(httpCode).c_str());
    

    http.begin(client, onlineURL);
    int onlineCode = http.GET();
    bool onlineWorked = (onlineCode > 0);
    http.end();

    if (onlineWorked) {
        return "OPI:OFF INET:ON (resolved here)";
    } else {
        return "OPI:OFF INET:OFF (resolved here)";
    }
  }
}

const char* mediaURL = EXTERNAL_MEDIA_URL;
String getMedia() {
  HTTPClient http;
  WiFiClient client;
  http.begin(client, mediaURL); // HTTP only, not HTTPS!
  int httpCode = http.GET();

  if (httpCode > 0) { // Check for the returning code
    if (httpCode == 404) {
        http.end();
        return ""; //will signal to skip this screen
    }
    String payload = http.getString();
    if (DEBUG) Serial.printf("Media payload: %s\n", payload.c_str());
    http.end();
    return payload;

  } else {
    http.end();
    // Throw an error or handle it as you wish
    Serial.printf("HTTP request failed, error: %s\n", http.errorToString(httpCode).c_str());
    // You can throw or return an empty string or error code
    return "Failed to fetch media :(";
  }
}

const char* testURL = "http://localhost/AOD/test";
String getTest() {
   HTTPClient http;
  WiFiClient client;
  http.begin(client, testURL); // HTTP only, not HTTPS!
  int httpCode = http.GET();

  if (httpCode > 0) { // Check for the returning code
    if (httpCode != 200) {
        http.end();
        return String();
    } else {
      String payload = http.getString();
      if (DEBUG) Serial.printf("Test payload: %s\n", payload.c_str());
      http.end();
      return payload;
    }
  } else {
    http.end();
    return String();
  }
}
