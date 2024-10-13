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
# print (CPU_temp)
ultrasonic_distance = round(px.ultrasonic.read(), 2);
power=0
car_direction='stop';
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

def bluetooth_thread():
    global s
    print ('thread running for bluetooth')
    data_snapshot:string='';
    tempDataSnapshot:string='';
    active_binding_status:bool=True;

    def data_received_handling(data):
        global bluetooth_thread_telemetry_thread_run, bluetooth_time_snapshot, wifi_time_snapshot
        data=data.strip()
        print ('data is: ', data)
        # CPU_temp=gpiozero.CPUTemperature().temperature;
        # ultrasonic_distance=round(px.ultrasonic.read(), 2)
        # dataObjectToSend= dataObject(CPU_temp, ultrasonic_distance)
        # if (data!=None):
        #     data_snapshot=data.strip();
        #     print ('data received for bluetooth connection is:', data)
        #     print (type(data))
        #     print ('data_snapshot received for bluetooth connection is:', data_snapshot.strip())
        #     print (type(data_snapshot))
        #     while (data_snapshot=='start telemetry' and data_snapshot!='stop telemetry'):
        #         try:
        #             # print(data_snapshot)
        #             data_snapshot=data.strip();
        #             current_time = monotonic_ns()
        #             time_elapsed=(current_time-start_time)/1000000000
        #             print('data_snapshot is:', data_snapshot)
        #             print (time_elapsed)
        #             print (time_elapsed%5)
        #             print (int(time_elapsed)%5)
        #             if (int(time_elapsed)%5==0):
        #                 dataObjectConstruction=dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
        #                 encoded_data_for_sendall=json.dumps(dataObjectConstruction)
        #                 s.send(encoded_data_for_sendall)
        #                 print ('command snapshot is: ', data_snapshot)
        #                 print ('time elapsed is: ', time_elapsed)
        #                 print ('data sent is: ', encoded_data_for_sendall)
        #         except Exception as e:
        #             print (e)
        #             break

        if (data=='start telemetry'):
            print ('starting telemetry for bluetooth')
            s.send('starting telemetry for bluetooth')
            bluetooth_time_snapshot=-1
            wifi_time_snapshot=-1
            bluetooth_thread_telemetry_thread_run=True;
            # t3.start()

        if (data=='stop telemetry'):
            print ('stopping telemetry for bluetooth')
            s.send('stopping telemetry for bluetooth')
            bluetooth_thread_telemetry_thread_run=False;
            # t3.join();

        if (data=='break'):
            print('breaking bluetooth connection')
            return

    def received_handler(data='connected'):
        # CPU_temp=gpiozero.CPUTemperature().temperature;
        # ultrasonic_distance=round(px.ultrasonic.read(), 2)
        # dataObjectToSend= dataObject(CPU_temp, ultrasonic_distance)
        # while active_binding_status:
        print ('received_handler running, starting t3 thread')
        t3.start();
        # if data_snapshot!=None and data_snapshot!='':
        #     print ('data_snapshot is: ', data_snapshot)
        # if data_snapshot=='start telemetry':
        #     try:
        #         print(data_snapshot)
        #         if (data_snapshot == b"start telemetry" and data_snapshot!= b"stop telemetry"):
        #             dataObjectConstruction=dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
        #             encoded_data_for_sendall=json.dumps(dataObjectConstruction)
        #             s.send(encoded_data_for_sendall)
        #             print ('data is: ', encoded_data_for_sendall)
        #     except Exception as e:
        #         return

    # s=BluetoothServer(data_received_callback=data_received_handling,when_client_connects=received_handler)
    s=BluetoothServer(data_received_callback=data_received_handling,when_client_connects=received_handler)
    pause()

def bluetooth_thread_telemetry():
    global s, bluetooth_thread_telemetry_thread_run, bluetooth_time_snapshot
    # print('bluetooth telemetry starting and running!')
    # s.send('bluetooth telemetry starting and running! Type stop telemetry to disable')
    CPU_temp=gpiozero.CPUTemperature().temperature;
    ultrasonic_distance=round(px.ultrasonic.read(), 2)
    # dataObjectToSend= dataObject(CPU_temp, ultrasonic_distance)
    dataObjectToSend=dataObject();
    while (True):
        try:
            global bluetooth_thread_telemetry_thread_run, bluetooth_time_snapshot, car_direction, power
            current_time = monotonic_ns()
            time_elapsed=(current_time-start_time)/1000000000
            # print (int(time_elapsed))
            # print (time_snapshot)
            # print (time_elapsed%5)
            # print ('before time comparison is: ', int(time_elapsed)%5)
            # if (bluetooth_thread_telemetry_thread_run==False):
                # s.send('telemetry stopped, type start telemetry to enable')
                # break;
            # print ('t3 running')
            if (bluetooth_thread_telemetry_thread_run==True):
                # print ('t3 switch is true')
                if (bluetooth_time_snapshot==-1):
                    dataObjectConstruction=dataObjectToSend.JSON_format(car_direction, power, gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                    encoded_data_for_sendall=json.dumps(dataObjectConstruction)
                    s.send(encoded_data_for_sendall)
                    # print ('data sent is: ', encoded_data_for_sendall)
                    bluetooth_time_snapshot=int(time_elapsed)+5

                if (bluetooth_time_snapshot==int(time_elapsed)):
                    # print ('sending data every 5 seconds!')
                    # print ('time elapsed is: ', time_elapsed)
                    # print ('modulo coparison is: ', (int(time_elapsed)%5)==0)
                    dataObjectConstruction=dataObjectToSend.JSON_format(car_direction, power, gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                    encoded_data_for_sendall=json.dumps(dataObjectConstruction)
                    s.send(encoded_data_for_sendall)
                    # print ('data sent is: ', encoded_data_for_sendall)
                    bluetooth_time_snapshot=int(time_elapsed)+5
                    # print ('time sanity check: ', int(time_elapsed), time_snapshot)

        except Exception as e:
            print (e)
            break 


def wifi_thread():
    global s_wifi, client, wifi_thread_telemetry_thread_run
    print ('thread running for wifi')
    HOST = "192.168.1.7" # IP address of your Raspberry PI
    PORT = 65432          # Port to listen on (non-privileged ports are > 1023)
    socket.socket(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s_wifi=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_wifi.bind((HOST, PORT))
    s_wifi.listen()
    client, clientInfo = s_wifi.accept()
    active_binding_status:bool=True;
    try:
        t4.start()
        while active_binding_status==True:
            global car_direction, power, bluetooth_time_snapshot, wifi_time_snapshot
            # print ('wifi main while loop running')
            # print("server recv from: ", clientInfo)
            if (client!=None):
                data = client.recv(1024)      # receive 1024 Bytes of message in binary format

            # if (data == b"start telemetry" and data!= b"stop telemetry"):
            #     #send telemetry data via wifi
            #     dataObjectConstruction=dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))                
            #     encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
            #     client.sendall(encoded_data_for_sendall)

            # if (data == b"start camera"):
            #     Vilib.camera_start(vflip=False,hflip=False)
            #     Vilib.display(local=False,web=True)

            # if (data==b"stop camera"):
            #     Vilib.camera_close()

            if data != b"":
                # print(data);
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

def wifi_thread_telemetry():
    active_binding_status:bool=True;
    CPU_temp=gpiozero.CPUTemperature().temperature;
    ultrasonic_distance=round(px.ultrasonic.read(), 2)
    # dataObjectToSend= dataObject(car_direction, power, CPU_temp, ultrasonic_distance)    
    dataObjectToSend=dataObject();
    print('wifi_thread for telemetry running')
    # try:
    #     while active_binding_status==True:
    #         # print ('wifi main while loop running')
    #         # print("server recv from: ", clientInfo)
    #         data = client.recv(1024)      # receive 1024 Bytes of message in binary format

    #         if (data == b"start telemetry" and data!= b"stop telemetry"):
    #             #send telemetry data via wifi
    #             dataObjectConstruction=dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))                
    #             encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
    #             client.sendall(encoded_data_for_sendall)
    while (True):
        try:
            global wifi_thread_telemetry_thread_run, wifi_time_snapshot, car_direction, power
            current_time = monotonic_ns()
            time_elapsed=(current_time-start_time)/1000000000
            # print (int(time_elapsed))
            # print (time_snapshot)
            # print (time_elapsed%5)
            # print ('before time comparison is: ', int(time_elapsed)%5)
            # if (bluetooth_thread_telemetry_thread_run==False):
                # s.send('telemetry stopped, type start telemetry to enable')
                # break;
            # print ('t3 running')
            if (wifi_thread_telemetry_thread_run==True and client!=None):
                # print ('wifi telemetry running')
                # print ('t3 switch is true')
                if (wifi_time_snapshot==-1):
                    dataObjectConstruction=dataObjectToSend.JSON_format(car_direction, power,gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                    encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
                    client.sendall(encoded_data_for_sendall)
                    print ('data sent is: ', encoded_data_for_sendall)
                    wifi_time_snapshot=int(time_elapsed)+3

                if (wifi_time_snapshot==int(time_elapsed)):
                    # print ('sending data every 5 seconds!')
                    # print ('time elapsed is: ', time_elapsed)
                    # print ('modulo coparison is: ', (int(time_elapsed)%5)==0)
                    dataObjectConstruction=dataObjectToSend.JSON_format(car_direction, power,gpiozero.CPUTemperature().temperature, round(px.ultrasonic.read(), 2))
                    encoded_data_for_sendall=json.dumps(dataObjectConstruction).encode()
                    client.sendall(encoded_data_for_sendall)
                    print ('data sent is: ', encoded_data_for_sendall)
                    wifi_time_snapshot=int(time_elapsed)+3
                    # print ('time sanity check: ', int(time_elapsed), time_snapshot)

            if (wifi_thread_telemetry_thread_run==False):
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

        # finally:
        #     print("Closing socket, program exited correctly")
        #     px.stop();
        #     client.sendall(b'closing connection from host')
        #     client.close()
        #     s_wifi.close()
    
def wifi_thread_camera():
    try:
        Vilib.camera_start(vflip=False,hflip=False)
        Vilib.display(local=False,web=True)
    
    except Exception as e:
        Vilib.camera_close()


if __name__ =="__main__":
    try:
        t1 = threading.Thread(target=bluetooth_thread,)
        t2 = threading.Thread(target=wifi_thread,)
        t3 = threading.Thread(target=bluetooth_thread_telemetry,)
        t4 = threading.Thread(target=wifi_thread_telemetry,)
        t5 = threading.Thread(target=wifi_thread_camera,)


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