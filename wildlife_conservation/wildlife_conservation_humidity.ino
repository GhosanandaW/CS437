#include "DHT.h"
#define DHTPIN 7
DHT dht(DHTPIN);

void setup() {
   Serial.begin(9600);
   dht.begin();
}


void loop() {
   bool isInCelcius = true;

   if (Serial.available() > 0) {	
      float h = dht.readHumidity() * 100; // Convert to %
      Serial.println("Humidity: " + to_string(h) + "%; ");
      float t = dht.readTemperature(isInCelcius);   
      Serial.println("Temperature: " + to_string(t));
   }
   else {
      
   }
   delay(1000);
}
