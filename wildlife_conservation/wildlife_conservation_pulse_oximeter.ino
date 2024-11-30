#include "PulseOximeter.h"
#define PULSE_OXI_PIN 2
PulseOximeter pox;


void setup() {
    pinMode(PULSE_OXI_PIN, INPUT);
    Serial.begin(9600);
}


void loop() {
    if (Serial.available() > 0){
    if (pox.begin()) {
        string hr=pox.getHeartRate();
        Serial.println(hr);
        string sp02=pox.getSpO2();
        Serial.println(sp02);
        }
            } 
    else {
    }
    delay(1000);
}
