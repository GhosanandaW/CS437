#include "Adafruit_GPS.h"
Adafruit_GPS GPS;

void setup() {
  Serial.begin(9600);
}
void loop() {
  if (Serial.available() > 0) {	
      string gpsResult = GPS.read();
      Serial.print(gpsResult);
  } else {
    
  }
  delay(100);
}