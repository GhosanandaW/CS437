int sensorPin = A0; // select the input pin for LDR
int sensorValue = -1; // variable to store the value coming from the sensor

void setup() {
Serial.begin(9600); //sets serial port for communication
}

void loop() {
    sensorValue = analogRead(sensorPin); // read the value from the sensor
    if (sensorValue >= 0) {	
        Serial.println(sensorValue); //prints the values coming from the sensor on the screen
    }
    else{
    }
    delay(1000);
}