from bluedot.btcomm import BluetoothServer
from signal import pause
import socket
import gpiozero
import json
from picarx import Picarx
import time

#PiCarX init and telemetry
px = Picarx()
CPU_temp:float = gpiozero.CPUTemperature().temperature;
# print (CPU_temp)
ultrasonic_distance = round(px.ultrasonic.read(), 2);

#data object to send
class dataObject:
    CPU_temp:float=0;
    ultrasonic_distance:float=0;

    def __init__(self, CPU_temp,ultrasonic_distance):
        self.CPU_temp = CPU_temp
        self.ultrasonic_distance=ultrasonic_distance
    
    def JSON_format(self,CPU_temp, ultrasonic_distance):
        self.CPU_temp=CPU_temp
        self.ultrasonic_distance=ultrasonic_distance
        return {"CPU_temp":self.CPU_temp, "ultrasonic_distance":self.ultrasonic_distance}
    
def received_handler(data='connected'):
    # print(data)
    # s.send(data)
    active_binding_status:bool=True;
    CPU_temp=gpiozero.CPUTemperature().temperature;
    ultrasonic_distance=round(px.ultrasonic.read(), 2)
    dataObjectToSend= dataObject(CPU_temp, ultrasonic_distance)
    # print ('going for the try block')
    while active_binding_status:
        try:
            # print ('inside try block')
            # while active_binding_status==True:
            # s.send('active binding running! Constantly sending data!')
            dataObjectConstruction=dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
            # print (dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature))

            # encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
            encoded_data_for_sendall=json.dumps(dataObjectConstruction)
            # s.send('constantly sending data!')
            # s.send(encoded_data_for_sendall)
            s.send(encoded_data_for_sendall)
            print ('data is: ', encoded_data_for_sendall)
            # print (type(encoded_data_for_sendall))
        except Exception as e: 
            # print (e)
            # print("Closing socket")
            # s.send('closing connection due to exception')
            break
        # finally:
            # print("Closing bluetooth, program exited correctly")
            # s.send('closing connection from host, exited correctly')



# s=BluetoothServer(when_client_connects=received_handler())
# pause()

s=BluetoothServer(data_received_callback=None,when_client_connects=received_handler)
pause()
