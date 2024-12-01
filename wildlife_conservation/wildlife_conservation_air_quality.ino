#include "MQ135.h"
MQ135 gasSensor = MQ135(A0);
void setup(){
  Serial.begin(9600);
}
void loop(){
  float ppm = gasSensor.getPPM();
  Serial.println(ppm);
  delay(1000);
}