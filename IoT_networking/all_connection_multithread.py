from bluedot.btcomm import BluetoothServer
from signal import pause
import socket
import gpiozero
import json
from picarx import Picarx
from vilib import Vilib #adapted and referenced from Sunfounder Vilib library: https://github.com/sunfounder/vilib
import threading
from time import sleep, time, strftime, localtime, monotonic_ns
import sys

#PiCarX init and telemetry
px = Picarx()
CPU_temp:float = gpiozero.CPUTemperature().temperature;
ultrasonic_distance = round(px.ultrasonic.read(), 2);
power=0
car_direction='stop';

#server and client connection init
start_time = monotonic_ns()
s=None
s_wifi=None
client=None
bluetooth_thread_telemetry_thread_run:bool=None;
wifi_thread_telemetry_thread_run:bool=None;
bluetooth_time_snapshot:int=-1;
wifi_time_snapshot:int=-1


#data object to send
class dataObject:
    global power, car_direction
    CPU_temp:float=0;
    ultrasonic_distance:float=0;

    def __init__(self):
        self.car_direction=car_direction
        self.power=power
        self.CPU_temp = CPU_temp
        self.ultrasonic_distance=ultrasonic_distance
    
    def JSON_format(self,car_direction, power, CPU_temp, ultrasonic_distance):
        self.car_direction=car_direction
        self.power=power
        self.CPU_temp=CPU_temp
        self.ultrasonic_distance=ultrasonic_distance
        return {"car_direction":self.car_direction, "power":self.power, "CPU_temp":self.CPU_temp, "ultrasonic_distance":self.ultrasonic_distance}

#Main bluetooth thread for setup and communication middle layer
def bluetooth_thread():
    global s
    print ('thread running for bluetooth')
    data_snapshot:string='';
    tempDataSnapshot:string='';
    active_binding_status:bool=True;

    def data_received_handling(data):
        global bluetooth_thread_telemetry_thread_run, bluetooth_time_snapshot, wifi_time_snapshot
        data=data.strip()

        if (data=='start telemetry'):
            print ('starting telemetry for bluetooth')
            s.send('starting telemetry for bluetooth')
            bluetooth_time_snapshot=-1
            wifi_time_snapshot=-1
            bluetooth_thread_telemetry_thread_run=True;

        if (data=='stop telemetry'):
            print ('stopping telemetry for bluetooth')
            s.send('stopping telemetry for bluetooth')
            bluetooth_thread_telemetry_thread_run=False;

        if (data=='break'):
            print('breaking bluetooth connection')
            return

    def received_handler(data='connected'):
        print ('received_handler running, starting t3 thread')
        t3.start();
    
    s=BluetoothServer(data_received_callback=data_received_handling,when_client_connects=received_handler)
    pause()

#Bluetooth telemetry thread controlled by bluetooth main thread
def bluetooth_thread_telemetry():
    global s, bluetooth_thread_telemetry_thread_run, bluetooth_time_snapshot
    
    #telemetry data init
    CPU_temp=gpiozero.CPUTemperature().temperature;
    ultrasonic_distance=round(px.ultrasonic.read(), 2)
    dataObjectToSend=dataObject();

    #telemetry data main loop
    while (True):
        try:
            global bluetooth_thread_telemetry_thread_run, bluetooth_time_snapshot, car_direction, power
            current_time = monotonic_ns()
            time_elapsed=(current_time-start_time)/1000000000

            #if telemetry switched to true = send data to all connected device
            #if telemetry switched to false = stop sending data
            if (bluetooth_thread_telemetry_thread_run==True):
                if (bluetooth_time_snapshot==-1):
                    dataObjectConstruction=dataObjectToSend.JSON_format(car_direction, power, gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                    encoded_data_for_sendall=json.dumps(dataObjectConstruction)
                    s.send(encoded_data_for_sendall)
                    bluetooth_time_snapshot=int(time_elapsed)+5

                if (bluetooth_time_snapshot==int(time_elapsed)):
                    dataObjectConstruction=dataObjectToSend.JSON_format(car_direction, power, gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                    encoded_data_for_sendall=json.dumps(dataObjectConstruction)
                    s.send(encoded_data_for_sendall)
                    bluetooth_time_snapshot=int(time_elapsed)+5

        except Exception as e:
            print (e)
            break 

#main wifi thread for controlling the wifi communication, the running thread, and car movement
def wifi_thread():
    global s_wifi, client, wifi_thread_telemetry_thread_run
    print ('thread running for wifi')

    #main setup for wifi communication between devices
    HOST = "192.168.1.7" # IP address of your Raspberry PI
    PORT = 65432          # Port to listen on (non-privileged ports are > 1023)
    socket.socket(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s_wifi=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_wifi.bind((HOST, PORT))
    s_wifi.listen()
    client, clientInfo = s_wifi.accept()
    active_binding_status:bool=True;

    #main loop for wifi_thread
    try:
        #t4 is video streaming thread directly from the car, needs to be started after the initial init above
        t4.start()
        while active_binding_status==True:
            global car_direction, power, bluetooth_time_snapshot, wifi_time_snapshot
            if (client!=None):
                data = client.recv(1024) # receive 1024 Bytes of message in binary format

            #main data logic to control movement of the car
            if data != b"":
                if data==b"88":
                    power=0
                    px.set_dir_servo_angle(0);
                    px.forward(0);
                    px.backward(0);
                    px.stop();
                    car_direction='stop'
                
                if data ==b"87":
                    px.set_dir_servo_angle(0)
                    power=10;
                    px.forward(power);
                    car_direction='forward'

                if data ==b"83":
                    px.set_dir_servo_angle(0)
                    power=10;
                    px.backward(power);
                    car_direction='backward'
                
                if data ==b"68":
                    px.set_dir_servo_angle(30)
                    power=10;
                    px.forward(power);
                    car_direction='right turn'
                
                if data ==b"65":
                    px.set_dir_servo_angle(-30)
                    power=10;
                    px.forward(power);
                    car_direction='left turn'
            
                if data==b"start telemetry":
                    print ('turning on telemetry')
                    bluetooth_time_snapshot=-1
                    wifi_time_snapshot=-1
                    wifi_thread_telemetry_thread_run=True
                
                if data==b"stop telemetry":
                    print ('stopping telemetry')
                    wifi_thread_telemetry_thread_run=False

            if data==b"break":
                active_binding_status=False;
    
    except: 
        print("Closing socket")
        px.stop();
        client.sendall(b'closing socket')
        client.close()
        s_wifi.close()

    finally:
        print("Closing socket, program exited correctly")
        px.stop();
        client.sendall(b'closing connection from host')
        client.close()
        s_wifi.close()

#thread dedicated to control telemetry communication between server and client
def wifi_thread_telemetry():
    #telemetry data init
    active_binding_status:bool=True;
    CPU_temp=gpiozero.CPUTemperature().temperature;
    ultrasonic_distance=round(px.ultrasonic.read(), 2)  
    dataObjectToSend=dataObject();
    print('wifi_thread for telemetry running')

    #main while loop to control if the server sending data or not to the client
    while (True):
        try:
            global wifi_thread_telemetry_thread_run, wifi_time_snapshot, car_direction, power
            current_time = monotonic_ns()
            time_elapsed=(current_time-start_time)/1000000000

            #if telemetry turned on and client connected, send data every 3 seconds
            if (wifi_thread_telemetry_thread_run==True and client!=None):
                if (wifi_time_snapshot==-1):
                    dataObjectConstruction=dataObjectToSend.JSON_format(car_direction, power,gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                    encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
                    client.sendall(encoded_data_for_sendall)
                    print ('data sent is: ', encoded_data_for_sendall)
                    wifi_time_snapshot=int(time_elapsed)+3

                if (wifi_time_snapshot==int(time_elapsed)):
                    dataObjectConstruction=dataObjectToSend.JSON_format(car_direction, power,gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                    encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
                    client.sendall(encoded_data_for_sendall)
                    print ('data sent is: ', encoded_data_for_sendall)
                    wifi_time_snapshot=int(time_elapsed)+3

            #if telemetry turned off and client connected, send all default zero data to client
            if (wifi_thread_telemetry_thread_run==False and client!=None):
                dataObjectConstruction=dataObjectToSend.JSON_format('stop',0,0,0)
                encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
                client.sendall(encoded_data_for_sendall)
                wifi_time_snapshot=-1
            
        except Exception as e: 
            print (e)
            print("Closing socket")
            px.stop();
            client.sendall(b'closing socket')
            client.close()
            s_wifi.close()

#main thread to start video streaming from the car
def wifi_thread_camera():
    try:
        Vilib.camera_start(vflip=False,hflip=False)
        Vilib.display(local=False,web=True)
    
    except Exception as e:
        Vilib.camera_close()


#main loop that run the thread
if __name__ =="__main__":
    try:
        #t1 is the thread to control bluetooth processes
        #t2 is the thread to control wifi processes
        #t3 is the thread to control bluetooth telemetry
        #t3 is the thread to control wifi telemetry
        #t5 is the thread to control camera video streaming processes

        t1 = threading.Thread(target=bluetooth_thread,)
        t2 = threading.Thread(target=wifi_thread,)
        t3 = threading.Thread(target=bluetooth_thread_telemetry,)
        t4 = threading.Thread(target=wifi_thread_telemetry,)
        t5 = threading.Thread(target=wifi_thread_camera,)

        #t5 being started first because it takes time to boot up
        t5.start()
        t1.start()
        t2.start()

        t5.join()
        t1.join()
        t2.join()
        t3.join()
        t4.join()


    except:
        print ('both thread 1+ thread 2 +thread 3 completed running')
        print ('closing program')
        sys.exit()