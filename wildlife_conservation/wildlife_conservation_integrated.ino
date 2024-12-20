//Pulse oximeter
#include "PulseOximeter.h"
#define PULSE_OXI_PIN 2
PulseOximeter pox;

//GPS
#include "Adafruit_GPS.h"
Adafruit_GPS GPS;

//air quality sensor
#include "MQ135.h"
MQ135 gasSensor = MQ135(A0);

//humidity and temperature sensor
#include "DHT.h"
#define DHTPIN 7
DHT dht(DHTPIN);

void setup() {
    pinMode(PULSE_OXI_PIN, INPUT);
    pinMode(1, OUTPUT);
    pinMode(8, INPUT);
    Serial.begin(9600);
    dht.begin();
}

void loop() {
    bool isInCelcius = true;

    if (Serial.available() > 0){
        Serial.println("");
        //pulseoximeter section
        if (pox.begin()) {
            string hr=pox.getHeartRate();
            Serial.println("Heart rate is: "+hr);
            string sp02=pox.getSpO2();
            Serial.println("Oxygen Saturation is: "+sp02);
            // get the readings and print them out
            }
        
        //gps section
        string gpsResult = GPS.read();
        Serial.println("gps location is: "+gpsResult);

        //air quality sensor section
        float ppm = gasSensor.getPPM();
        Serial.print("PPM is: ");
        Serial.println(ppm);

        int digitalResult = digitalRead(8);
        if (digitalResult == HIGH) {
            Serial.println("Gas DETECTED!");
            }
        else {
            Serial.println("Gas not detected");
        }

        //humidity and temperature sensor section
        float h = dht.readHumidity() * 100; // Convert to %
        Serial.println("Humidity: " + to_string(h) + "%; ");
        float t = dht.readTemperature(isInCelcius);   
        Serial.println("Temperature: " + to_string(t));

        //end of sensor reading
        Serial.println("--- END OF SENSOR READING FROM MAIN LOOP ---");

        //check for gossip message
        if (Serial.availableMessage() != 0) {
            string mystr = Serial.readMessage();
            Serial.println("Printed by receiver:" + mystr);
        }

        //transmit gossip information
        string msg = "Hello from a Zebra!";
        Serial.sendMessage(1, msg);
        Serial.println("");


        //end of sensor reading
        Serial.println("--- END OF GOSSIP ALGORITHM FROM MAIN LOOP ---");
    } 
    else {
    }
    delay(1000);
}
