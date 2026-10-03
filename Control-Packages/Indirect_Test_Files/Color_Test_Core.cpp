#include <Arduino.h>

#define RGB_LED_PIN 48  // Change to 38 if using DevKitM-1

void processKey(char c) {
    switch (c) {
        case 'R': neopixelWrite(RGB_LED_PIN, 255, 0, 0); break; // Red ON
        case 'G': neopixelWrite(RGB_LED_PIN, 0, 255, 0); break; // Green ON
        case 'B': neopixelWrite(RGB_LED_PIN, 0, 0, 255); break; // Blue ON
        case 'r':
        case 'g':
        case 'b': neopixelWrite(RGB_LED_PIN, 0, 0, 0);   break; // OFF on release
    }
}

void setup() {
    Serial.begin(115200);
    Serial0.begin(115200);
    neopixelWrite(RGB_LED_PIN, 0, 0, 0);
}

void loop() {
    if (Serial.available() > 0)  processKey((char)Serial.read());
    if (Serial0.available() > 0) processKey((char)Serial0.read());
}
