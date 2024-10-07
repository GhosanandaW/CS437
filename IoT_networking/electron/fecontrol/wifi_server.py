import socket
import gpiozero
import json

HOST = "192.168.1.9" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)
socket.socket(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#telemetry
CPU_temp:float = gpiozero.CPUTemperature().temperature;
print (CPU_temp)

#data object to send
class dataObject:
    CPU_temp:float=0;

    def __init__(self, CPU_temp):
        self.CPU_temp = CPU_temp
    
    def JSON_format(self,CPU_temp):
        self.CPU_temp=CPU_temp
        return {"CPU_temp":self.CPU_temp}



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    active_binding_status:bool=True;
    CPU_temp=gpiozero.CPUTemperature().temperature;
    dataObjectToSend= dataObject(CPU_temp)
    
    try:
        while active_binding_status==True:
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)

            dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature)
            print (dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature))

            data = client.recv(1024)      # receive 1024 Bytes of message in binary format
            # if data != b"":
            #     print(data)
            #     client.sendall(data) # Echo back to client
            print (json.dumps(dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature)))
            # encoded_data_for_sendall=json.dumps(dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature)).encode()
            encoded_data_for_sendall=json.dumps(dataObjectToSend.JSON_format(gpiozero.CPUTemperature().temperature)).encode()
            client.sendall(encoded_data_for_sendall)

            if data==b"break\r\n":
                active_binding_status=False;
    
    except: 
        print("Closing socket")
        client.sendall('closing socket')
        client.close()
        s.close()

    finally:
        print("Closing socket, program exited correctly")
        client.sendall(b'closing connection from host')
        client.close()
        s.close() 