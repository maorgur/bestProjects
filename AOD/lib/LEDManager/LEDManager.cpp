#include <ScreenManager.hpp>

#include <FastLED.h>
#define LED_PIN 13
#define NUM_LEDS 96
#define READY_SIGNAL 0x01
#define UPDATE_TIMEOUT 5000

CRGB leds[NUM_LEDS];
static uint8_t frameBuf[NUM_LEDS * 3];

void LEDSetup() {
  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.clear(true);
  Serial.print(READY_SIGNAL);
}

void LEDTurnOff() {
  FastLED.clear(true);
}

void LEDLoop(Screen currentScreen) {
    //would handle LED on loop (that way, will "block" the other code from executing)
    //when no more info is sent, it will exit, and will return if it even ran once
    if (!Serial.available()){
        return;
    } else {
        currentScreen.turnOff();
    }

    long lastUpdate = millis();
    while (millis() - lastUpdate < UPDATE_TIMEOUT){
        if (!Serial.available()){
            continue;
        }
        int b = Serial.read();
        if (b == '>') {
          lastUpdate = millis();
          // Read exactly NUM_LEDS*3 bytes into frameBuf
          size_t needed = sizeof(frameBuf);
          size_t got = Serial.readBytes(reinterpret_cast<char*>(frameBuf), needed);
          if (got == needed) {
            // Map bytes to LEDs (RGB order)
            for (int i = 0; i < NUM_LEDS; i++) {
              uint8_t r = frameBuf[i * 3 + 0];
              uint8_t g = frameBuf[i * 3 + 1];
              uint8_t b = frameBuf[i * 3 + 2];
              leds[i] = CRGB(r, g, b);
            }
            FastLED.show();
            Serial.print(READY_SIGNAL);
          }
          // If not enough bytes arrived (timeout), drop partial frame and resync
          else {
            delay(1);
          }
    }
  }
  currentScreen.turnOn();
  return;
}
