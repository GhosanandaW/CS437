from pydoc import text
from vilib import Vilib
from time import sleep, time, strftime, localtime
import threading
import readchar
import os

flag_face = False
flag_color = False
qr_code_flag = False
flag_traffic_sign=False

manual = '''
Input key to call the function!
    q: Take photo
    1: Color detect : red
    2: Color detect : orange
    3: Color detect : yellow
    4: Color detect : green
    5: Color detect : blue
    6: Color detect : purple
    7: Traffic sign detection
    0: Switch off Color detect
    r: Scan the QR code
    f: Switch ON/OFF face detect
    s: Display detected object information
'''

color_list = ['close', 'red', 'orange', 'yellow',
        'green', 'blue', 'purple',
]

def face_detect(flag):
    print("Face Detect:" + str(flag))
    Vilib.face_detect_switch(flag)

def traffic_sign_detect(flag):
    print("traffic_sign Detect:" + str(flag))
    Vilib.traffic_detect_switch(flag)

def qrcode_detect():
    global qr_code_flag
    if qr_code_flag == True:
        Vilib.qrcode_detect_switch(True)
        print("Waitting for QR code")

    text = None
    while True:
        temp = Vilib.detect_obj_parameter['qr_data']
        if temp != "None" and temp != text:
            text = temp
            print('QR code:%s'%text)
        if qr_code_flag == False:
            break
        sleep(0.5)
    Vilib.qrcode_detect_switch(False)


def take_photo():
    _time = strftime('%Y-%m-%d-%H-%M-%S',localtime(time()))
    name = 'photo_%s'%_time
    username = os.getlogin()

    path = f"/home/{username}/Pictures/"
    Vilib.take_photo(name, path)
    print('photo save as %s%s.jpg'%(path,name))

def object_show():
    global flag_color, flag_face, flag_traffic_sign

    if flag_color is True:
        if Vilib.detect_obj_parameter['color_n'] == 0:
            print('Color Detect: None')
        else:
            color_coodinate = (Vilib.detect_obj_parameter['color_x'],Vilib.detect_obj_parameter['color_y'])
            color_size = (Vilib.detect_obj_parameter['color_w'],Vilib.detect_obj_parameter['color_h'])
            print("[Color Detect] ","Coordinate:",color_coodinate,"Size",color_size)

    if flag_face is True:
        if Vilib.detect_obj_parameter['human_n'] == 0:
            print('Face Detect: None')
        else:
            human_coodinate = (Vilib.detect_obj_parameter['human_x'],Vilib.detect_obj_parameter['human_y'])
            human_size = (Vilib.detect_obj_parameter['human_w'],Vilib.detect_obj_parameter['human_h'])
            print("[Face Detect] ","Coordinate:",human_coodinate,"Size",human_size)

    if flag_traffic_sign is True:
        print ('flag_traffic_sign at main triggered')
        if Vilib.detect_obj_parameter['traffic_sign_acc'] != 0:
            print('traffic_sign detected: '+str(Vilib.detect_obj_parameter['traffic_sign_acc']))
            take_photo()
        else:
            print('traffic_sign detected: '+str(Vilib.detect_obj_parameter['traffic_sign_acc']))
            traffic_sign_type=Vilib.detect_obj_parameter['traffic_sign_t']
            traffic_sign_coodinate = (Vilib.detect_obj_parameter['traffic_sign_x'],Vilib.detect_obj_parameter['traffic_sign_y'])
            traffic_sign_size = (Vilib.detect_obj_parameter['traffic_sign_w'],Vilib.detect_obj_parameter['traffic_sign_h'])
            print("[traffic_sign Detect] ","Coordinate:",traffic_sign_coodinate,"Size",traffic_sign_size)
            print('traffic sign type is: '+ str(traffic_sign_type))



def main():
    global flag_face, flag_color, qr_code_flag, flag_traffic_sign
    qrcode_thread = None

    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    print(manual)

    while True:
        # readkey
        key = readchar.readkey()
        key = key.lower()
        # take photo
        if key == 'q':
            take_photo()
        # color detect
        elif key != '' and key in ('0123456'):  # '' in ('0123') -> True
            index = int(key)
            if index == 0:
                flag_color = False
                Vilib.color_detect('close')
            else:
                flag_color = True
                Vilib.color_detect(color_list[index]) # color_detect(color:str -> color_name/close)
            print('Color detect : %s'%color_list[index])
        # face detection
        elif key =="f":
            flag_face = not flag_face
            face_detect(flag_face)
        
        elif key =="t":
            flag_traffic_sign = not flag_traffic_sign
            traffic_sign_detect(flag_traffic_sign)
        
        # qrcode detection
        elif key =="r":
            qr_code_flag = not qr_code_flag
            if qr_code_flag == True:
                if qrcode_thread == None or not qrcode_thread.is_alive():
                    qrcode_thread = threading.Thread(target=qrcode_detect)
                    qrcode_thread.daemon = True
                    qrcode_thread.start()
            else:
                if qrcode_thread != None and qrcode_thread.is_alive():
                # wait for thread to end
                    qrcode_thread.join()
                    print('QRcode Detect: close')
        # show detected object information
        elif key == "s":
            object_show()
        
        elif key == "/":
            exit()

        sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print ('exception triggered: ', e)
    finally:
        print("stop and exit")
        Vilib.camera_close()