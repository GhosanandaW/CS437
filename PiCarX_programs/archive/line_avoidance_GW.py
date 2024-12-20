from picarx import Picarx
import time


#init pycar class
px = Picarx()

#init line reference
# px.set_line_reference([432.0, 493.0, 385.0])
# px.set_line_reference([830, 850, 830])
# px.set_line_reference([820, 850, 820])
# px.set_line_reference([800,800,800])
px.set_line_reference([900, 900, 900])



#init for distance mapping
POWER = 10
SafeDistance = 30   # > 40 safe
DangerDistance = 10 # > 20 && < 40 turn around, 
                    # < 20 backward
direction_choices_dictionary={}
#init for line tracking
current_state=None
offset=20
last_state='forward'

def sweep_cam_pan_servo(self, servo_step=30, delay=1):
    """
    Sweeps the camera pan servo from min to max angle with a specified speed and delay.
    """
    self.set_cam_pan_angle(0)
    self.set_cam_tilt_angle(0)

    for angle in range(self.CAM_PAN_MIN+10, self.CAM_PAN_MAX-10, servo_step):
        self.set_cam_pan_angle(angle)
        distance = round(self.ultrasonic.read(), 2)
        direction_choices_dictionary[angle]=distance
        time.sleep(delay)
    
    self.set_cam_pan_angle(0)
    print ('direction_choices_dictionary is: ', direction_choices_dictionary)
    time.sleep(delay)
    self.cam_pan.pulse_width_percent(0)
    self.cam_tilt.pulse_width_percent(0)
    # Sweep back in reverse direction
    # for angle in range(self.CAM_PAN_MAX, self.CAM_PAN_MIN+1, -servo_step):
    #     self.set_cam_pan_angle(angle)
    #     time.sleep(delay)

def spin_to_scan(self):
    print ('no safe path ahead, spinning to scan other direction')
    # self.backward(POWER)
    # time.sleep(1)
    self.backward(0)
    time.sleep(1)
    self.set_dir_servo_angle(-30)
    self.backward(20)
    time.sleep(1)

def get_status(val_list): #check where there is no line
    _state = px.get_line_status(val_list)  # [bool, bool, bool], 0 means line, 1 means background and lower than threshold == 1
    print (val_list,_state)
    if _state == [1, 1, 1]:
        return 'forward'
    if _state == [0, 1, 1]:
        return 'right'
    if _state == [1, 0, 1]: #2 background vs 1 line, might be noise, choose left by default 
        return 'left'
    if _state == [1, 1, 0]:
        return 'left'
    if _state == [0, 0, 1]:
        return 'right'
    if _state == [0, 1, 0]:
        return 'forward'
    if _state == [1, 0, 0]:
        return 'left'
    if _state == [0,0,0]:
        return 'stop'

    # if sum(_state) == 3:
    #     return 'forward'
    # if sum(_state) <3:
    #     return 'stop'

    # if _state == [1, 1, 1]:
    #     return 'forward'
    # if _state == [0, 1, 1]:
    #     return 'right'
    # if _state == [1, 0, 1]:
    #     return 'stop'
    # if _state == [1, 1, 0]:
    #     return 'left'
    # if _state == [0, 0, 1]:
    #     return 'stop'
    # if _state == [0, 1, 0]:
    #     return 'stop'
    # if _state == [1, 0, 0]:
    #     return 'stop'
    # if _state == [0,0,0]:
    #     return 'stop'

# def get_status(val_list): #check where there is no line
#     _state = px.get_line_status(val_list)  # [bool, bool, bool], 0 means track, 1 means offtrack, offtrack will be triggered above threshold
#     print (val_list,_state)
#     if _state == [1, 1, 1]:
#         return 'stop'
#     if _state == [0, 1, 1]:
#         return 'left'
#     if _state == [1, 0, 1]: #2 background vs 1 line, might be noise, choose left by default 
#         return 'forward'
#     if _state == [1, 1, 0]:
#         return 'right'
#     if _state == [0, 0, 1]:
#         return 'left'
#     if _state == [0, 1, 0]:
#         return 'right'
#     if _state == [1, 0, 0]:
#         return 'right'
#     if _state == [0,0,0]:
#         return 'forward'

def outHandle(): #handle out of line by coming where the car moved from, until cleared off the line
    print('outHandle triggered')
    global last_state, current_state
    px.forward(0)
    px.backward(0)
    if last_state == 'forward' or current_state=='stop':
        # px.backward(10)
        # time.sleep(0.5)
        print('forward outhandle triggered')
        px.set_dir_servo_angle(0)
        px.backward(10)
        time.sleep(0.5)
        #try to wiggle for better reading
        # px.set_dir_servo_angle(-10)
        # px.backward(10)
        # time.sleep(0.3)
        px.set_dir_servo_angle(20)
        px.backward(10)
        time.sleep(0.5)
        current_state_val_list = px.get_grayscale_data()
        current_state = get_status(current_state_val_list)
        if current_state=='stop': #if double triggered and still stuck, rotate more
            px.set_dir_servo_angle(0)
            px.set_dir_servo_angle(20)
            px.backward(10)
            time.sleep(1)

        px.set_dir_servo_angle(0)
        px.forward(POWER+10)
        time.sleep(0.2) #change trajectory
        px.backward(0)
        
    if last_state == 'left':
        print('left outhandle triggered, hardbackup from left side')
        px.set_dir_servo_angle(0)
        px.set_dir_servo_angle(30)
        px.backward(10)
        time.sleep(1)
        px.set_dir_servo_angle(0)
        px.backward(10)
        time.sleep(0.5)
        px.backward(0)
    elif last_state == 'right':
        print('right outhandle triggered, hardbackup from right side')
        px.set_dir_servo_angle(0)
        px.set_dir_servo_angle(-30)
        px.backward(10)
        time.sleep(1)
        px.set_dir_servo_angle(0)
        px.backward(10)
        time.sleep(0.5)
        px.backward(0)

    # while True:
    #     gm_val_list = px.get_grayscale_data()
    #     gm_state = get_status(gm_val_list)
    #     print("outHandle gm_val_list: %s, %s"%(gm_val_list, gm_state))
    #     currentSta = gm_state
    #     if currentSta != 'stop':
    #         break
    time.sleep(0.001)

def normalHandle(): #handle out of line by coming where the car moved from, until cleared off the line; normal handle will try to steer clear instead of stopping and retreat
    global last_state, current_state
    # if last_state == 'forward' or current_state=='stop':
    #     # px.backward(10)
    #     # time.sleep(0.5)
    #     print('forward normalhandle triggered')
    #     px.set_dir_servo_angle(0)
    #     px.backward(10)
    #     time.sleep(0.5)
    #     #try to wiggle for better reading
    #     px.set_dir_servo_angle(-20)
    #     px.backward(10)
    #     time.sleep(0.6)
    #     px.forward(POWER)
    #     time.sleep(0.2) #change trajectory
    #     # px.set_dir_servo_angle(10)
    #     # px.backward(10)
    #     # time.sleep(0.5)
    #     px.backward(0)
    if last_state == 'left':
        print('left normalHandle triggered')
        px.set_dir_servo_angle(0)
        px.set_dir_servo_angle(-30)
        px.forward(20)
        time.sleep(0.8)
        px.set_dir_servo_angle(0)
        px.forward(20)
        time.sleep(0.3)
        px.forward(0)

    elif last_state == 'right':
        print('right outhandle triggered')
        px.set_dir_servo_angle(0)
        px.set_dir_servo_angle(30)
        px.forward(20)
        time.sleep(0.8)
        px.set_dir_servo_angle(0)
        px.forward(20)
        time.sleep(0.3)
        px.forward(0)

    # while True:
    #     gm_val_list = px.get_grayscale_data()
    #     gm_state = get_status(gm_val_list)
    #     print("outHandle gm_val_list: %s, %s"%(gm_val_list, gm_state))
    #     currentSta = gm_state
    #     if currentSta != 'stop':
    #         break
    time.sleep(0.001)


def main():
    try:
        no_safe_path_counter=0
        start_time = time.monotonic()

        # Do something that takes time
        # time.sleep(3.0 - ((time.monotonic() - starttime) % 3.0))
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
        px.set_dir_servo_angle(0)
        px.set_cam_tilt_angle(0)
        px.set_cam_pan_angle(0)
        px.forward(POWER)
        global last_state, current_state
        

        while True:
            #read time
            end_time = time.monotonic()
            elapsed_time = int(end_time - start_time)
            print("Elapsed time:", elapsed_time, "seconds")
            #read distance 
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ",distance)
            #read greyscale/line
            gm_val_list = px.get_grayscale_data()
            gm_state = get_status(gm_val_list)
            print("gm_val_list: %s, %s"%(gm_val_list, gm_state))


            #go forward
            #check for black line

            if (gm_state == "stop"):
                last_state = gm_state
                print('gm_state==stop hit ', gm_state)
                px.forward(0)
                px.backward(0)
                time.sleep(1)
                outHandle()
                current_state_val_list = px.get_grayscale_data()
                current_state = get_status(current_state_val_list)


            elif (gm_state == "left" or gm_state == "right"):
                last_state = gm_state
                normalHandle()
                px.set_dir_servo_angle(0)
                px.forward(POWER)
                current_state_val_list = px.get_grayscale_data()
                current_state = get_status(current_state_val_list)
                if current_state==last_state:
                    px.forward(0)
                    px.backward(0)
                    time.sleep(1)
                    outHandle()

            elif gm_state == "forward":
                print('gm_state!=stop hit', gm_state)
                last_state = gm_state
                print('moving forward in main')
                px.set_dir_servo_angle(0)
                px.forward(POWER)
                time.sleep (0.1)

            # px.forward(POWER)
            # time.sleep (0.2)
                # if gm_state == 'forward':
                #     px.set_dir_servo_angle(0)
                #     px.backward(POWER)
                # elif gm_state == 'left':
                #     px.set_dir_servo_angle(offset)
                #     px.backward(POWER)
                # elif gm_state == 'right':
                #     px.set_dir_servo_angle(-offset)
                #     px.forward(POWER)
                # else:
                #     outHandle()     

            # if gm_state == 'forward':
            #     print('moving forward')
            #     px.set_dir_servo_angle(0)
            #     px.forward(POWER)
            # elif gm_state == 'left':
            #     print('moving left')
            #     px.set_dir_servo_angle(-offset)
            #     px.forward(POWER)
            # elif gm_state == 'right':
            #     print('moving right')
            #     px.set_dir_servo_angle(offset)
            #     px.forward(POWER)
            # else:
            #     outHandle()

            # #check for distance and avoidance logic
            # #sanity check for blind spot
            # # px.set_cam_pan_angle(-30)
            # # time.sleep(0.5)
            # # px.set_cam_pan_angle(0)
            # # time.sleep(0.5)
            # # px.set_cam_pan_angle(30)

            # # print ('entering time monotonic check for cam angle')
            # if (elapsed_time%3.0==0):
            #     px.set_cam_pan_angle(-30)
            # elif (elapsed_time%5.0==0):
            #     px.set_cam_pan_angle(30)
            # else:
            #     px.set_cam_pan_angle(0)

            # print ('going into self driving mode')
            # if (distance<0):
            #     # px.forward(0)
            #     # px.backward(0)
            #     # sweep_cam_pan_servo(px);
            #     # temp_new_dir_min_angle=min(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with smallest distance
            #     # temp_new_dir_max_angle=max(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with largest distance
            #     # temp_new_dir_min_distance=direction_choices_dictionary[temp_new_dir_min_angle]
            #     # temp_new_dir_max_distance=direction_choices_dictionary[temp_new_dir_max_angle]
            #     # print(temp_new_dir_min_angle,temp_new_dir_min_distance)
            #     # print(temp_new_dir_max_angle,temp_new_dir_max_distance)
            #     # px.set_dir_servo_angle(temp_new_dir_max_angle)
            #     # px.forward(POWER)
            #     # time.sleep(1)
            #     # px.set_dir_servo_angle(-10) 
            #     #reading issue, try to wiggle for reading calib
            #     px.set_cam_pan_angle(-15)
            #     px.set_cam_pan_angle(0)
            #     px.set_cam_pan_angle(15)
            #     px.set_cam_pan_angle(0)
                
            # if (no_safe_path_counter>=3):
            #     print ('no safe path, high possibility of being stuck, call HELP!!!')
            #     px.set_dir_servo_angle(0)
            #     px.forward(0)
            #     return False;
        
            # # if distance <0:
            # #     print('negative distance dinged')
            # #     no_safe_path_counter=0
            # #     px.set_cam_pan_angle(0)
            # #     px.set_dir_servo_angle(0)
            # #     px.forward(POWER)
            # #     #sanity check for blind spot
            # #     px.set_cam_pan_angle(-30)
            # #     if (distance>0):
            # #         px.set_dir_servo_angle(-30)
            # #         px.forward(POWER)
            # #     px.set_cam_pan_angle(30)
            # #     if (distance>0):
            # #         px.set_dir_servo_angle(30)
            # #         px.forward(POWER)
            # #     print('negative distance dinged second time')
            # # px.set_dir_servo_angle(0)
            # # return False
            # elif (distance >= SafeDistance and distance>0):
            #     print('distance >= SafeDistance dinged')
            #     no_safe_path_counter=0
            #     px.set_dir_servo_angle(0)
            #     px.forward(POWER)
            #     #sanity check for blind spot
            #     # px.set_cam_pan_angle(-30)
            #     # time.sleep(0.5)
            #     # px.set_cam_pan_angle(0)
            #     # time.sleep(0.5)
            #     # px.set_cam_pan_angle(30)
            # elif (distance >= DangerDistance and distance>0):
            #     print('distance >= DangerDistance dinged')
            #     no_safe_path_counter=no_safe_path_counter+1
            #     px.forward(0)
            #     time.sleep(1)
            #     px.backward(POWER)
            #     time.sleep(1)
            #     px.backward(0)
            #     sweep_cam_pan_servo(px);
            #     temp_new_dir_min_angle=min(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with smallest distance
            #     temp_new_dir_max_angle=max(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with largest distance
            #     temp_new_dir_min_distance=direction_choices_dictionary[temp_new_dir_min_angle]
            #     temp_new_dir_max_distance=direction_choices_dictionary[temp_new_dir_max_angle]
            #     print(temp_new_dir_min_angle,temp_new_dir_min_distance)
            #     print(temp_new_dir_max_angle,temp_new_dir_max_distance)
            #     time.sleep(0.5)
            #     px.backward(0)
            #     # if (temp_new_dir_min_value<0):
            #     #     px.set_dir_servo_angle(temp_new_dir_min)
            #     # else:
            #     #     px.set_dir_servo_angle(temp_new_dir_max)
            #     px.set_dir_servo_angle(temp_new_dir_max_angle)
            #     px.forward(POWER)
            #     time.sleep(1) #run forward first for 2 seconds and recheck
            #     distance = round(px.ultrasonic.read(), 2)
            #     if (distance > SafeDistance): #if obstacle cleared, move forward 
            #         print('distance < SafeDistance dinged, moving forward')
            #         px.forward(0)
            #         px.set_dir_servo_angle(0)
            #         px.forward(POWER)
            #         distance = round(px.ultrasonic.read(), 2)
            #         # time.sleep(2)
            #     # time.sleep(2)
            #     elif (distance < SafeDistance): #if still encounter obstacle, spin another direction to look for more options to go for
            #         print('distance < SafeDistance dinged, moving to other direcitons')
            #         px.forward(0)
            #         time.sleep(1)
            #         spin_to_scan(px)
            #         no_safe_path_counter=no_safe_path_counter+1
            #         distance = round(px.ultrasonic.read(), 2)

            # elif (distance < DangerDistance and distance>0):
            #     print('distance < DangerDistance dinged')
            #     no_safe_path_counter=no_safe_path_counter+1
            #     print ('DANGER ZONE!!! BACK UP!!!')
            #     px.set_dir_servo_angle(0)
            #     px.backward(0)
            #     time.sleep(1)
            #     # px.set_dir_servo_angle(-45)
            #     px.backward(POWER)
            #     time.sleep(2)
            #     px.backward(0)
            #     #look for a better direction to go to
            #     distance = float(round(px.ultrasonic.read(), 2))
            #     print("distance: ",distance)
            #     sweep_cam_pan_servo(px);
            #     temp_new_dir_min_angle=min(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with smallest distance
            #     temp_new_dir_max_angle=max(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with largest distance
            #     temp_new_dir_min_distance=direction_choices_dictionary[temp_new_dir_min_angle]
            #     temp_new_dir_max_distance=direction_choices_dictionary[temp_new_dir_max_angle]
            #     print(temp_new_dir_min_angle,temp_new_dir_min_distance)
            #     print(temp_new_dir_max_angle,temp_new_dir_max_distance)
            #     time.sleep(0.5)
            #     px.backward(0)
            #     # if (temp_new_dir_min_value<0):
            #     #     px.set_dir_servo_angle(temp_new_dir_min)
            #     # else:
            #     #     px.set_dir_servo_angle(temp_new_dir_max)
            #     px.set_dir_servo_angle(temp_new_dir_max_angle)
            #     px.forward(POWER)
            #     time.sleep(1) #run forward first for 1 seconds and recheck
            #     distance = float(round(px.ultrasonic.read(), 2))
            #     if (distance > DangerDistance and distance>0): #if obstacle cleared, move forward 
            #         print('distance > DangerDistance dinged, moving forward')
            #         px.forward(0)
            #         px.set_dir_servo_angle(temp_new_dir_max_angle)
            #         px.forward(POWER)
            #         # time.sleep(2)
            #         distance = round(px.ultrasonic.read(), 2)

            #     # time.sleep(2)
            #     elif (distance < DangerDistance and distance>0): #if still within danger distance, look for other options to go for
            #         print('distance < DangerDistance dinged second time, spinning')
            #         spin_to_scan(px)
            #         no_safe_path_counter=no_safe_path_counter+1
            #         distance = round(px.ultrasonic.read(), 2)

            # # elif distance <0:
            # #     px.forward(0)
            # #     px.set_dir_servo_angle(30)
            # #     px.forward(0)
            #     # return False

    finally:
        print('finally hit')
        px.forward(0)
        px.backward(0)
        return False
        # if distance <0:
        #     px.forward(0)
        #     px.set_dir_servo_angle(0)
        #     return False


if __name__ == "__main__":
    main()

