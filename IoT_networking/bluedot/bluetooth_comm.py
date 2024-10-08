from bluedot.btcomm import BluetoothServer
from signal import pause

def received_handler(data):
    print(data)
    s.send(data)
    print ('data is: ', data)
    print (type(data))

s=BluetoothServer(received_handler)

pause()