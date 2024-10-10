from bluedot.btcomm import BluetoothServer
from signal import pause
import socket
import gpiozero
import json
from picarx import Picarx
import time
import threading

def bluetooth_thread():
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
        active_binding_status:bool=True;
        CPU_temp=gpiozero.CPUTemperature().temperature;
        ultrasonic_distance=round(px.ultrasonic.read(), 2)
        dataObjectToSend= dataObject(CPU_temp, ultrasonic_distance)
        while active_binding_status:
            try:
                dataObjectConstruction=dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                encoded_data_for_sendall=json.dumps(dataObjectConstruction)
                s.send(encoded_data_for_sendall)
                print ('data is: ', encoded_data_for_sendall)
            except Exception as e: 
                break

    s=BluetoothServer(data_received_callback=None,when_client_connects=received_handler)
    pause()

def wifi_thread():
    HOST = "192.168.1.7" # IP address of your Raspberry PI
    PORT = 65432          # Port to listen on (non-privileged ports are > 1023)
    socket.socket(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    #PiCarX init and telemetry
    px = Picarx()
    CPU_temp:float = gpiozero.CPUTemperature().temperature;
    print (CPU_temp)
    ultrasonic_distance = round(px.ultrasonic.read(), 2);
    power=10

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



    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        active_binding_status:bool=True;
        CPU_temp=gpiozero.CPUTemperature().temperature;
        ultrasonic_distance=round(px.ultrasonic.read(), 2)
        dataObjectToSend= dataObject(CPU_temp, ultrasonic_distance)
        
        try:
            while active_binding_status==True:
                client, clientInfo = s.accept()
                print("server recv from: ", clientInfo)

                dataObjectConstruction=dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))

                data = client.recv(1024)      # receive 1024 Bytes of message in binary format
                encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
                client.sendall(encoded_data_for_sendall)

                if data != b"":
                    print(data);
                    if data==b"88":
                        px.set_dir_servo_angle(0);
                        px.forward(0);
                        px.backward(0);
                        px.stop();
                    
                    if data ==b"87":
                        px.set_dir_servo_angle(0)
                        px.forward(power);

                    if data ==b"83":
                        px.set_dir_servo_angle(0)
                        px.backward(power);

                    
                    if data ==b"68":
                        px.set_dir_servo_angle(30)
                        px.forward(power);

                    
                    if data ==b"65":
                        px.set_dir_servo_angle(-30)
                        px.forward(power);

                if data==b"break":
                    active_binding_status=False;
        
        except: 
            print("Closing socket")
            px.stop();
            client.sendall(b'closing socket')
            client.close()
            s.close()

        finally:
            print("Closing socket, program exited correctly")
            px.stop();
            client.sendall(b'closing connection from host')
            client.close()
            s.close() 

if __name__ =="__main__":
    try:
        t1 = threading.Thread(target=bluetooth_thread)
        t2 = threading.Thread(target=wifi_thread)

        t1.start()
        t2.start()
    except:
        print ('both thread 1/2 completed running')
        print ('closing program')
        
    

