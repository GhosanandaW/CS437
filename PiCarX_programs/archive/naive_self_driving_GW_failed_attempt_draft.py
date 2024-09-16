from picarx import Picarx
import time

#init pycar class
px = Picarx()

#init for distance mapping
POWER = 20
SafeDistance = 30   # > 40 safe
DangerDistance = 10 # > 20 && < 40 turn around, 
                    # < 20 backward
direction_choices_dictionary={}
#init for line tracking
current_state=None
offset=20
last_state='stop'

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

def get_status(val_list): #check where the line position is, to run outhandling
    _state = px.get_line_status(val_list)  # [bool, bool, bool], 0 means line, 1 means background
    if _state == [0, 0, 0]:
        return 'stop'
    elif _state[1] == 1:
        return 'forward'
    elif _state[0] == 1:
        return 'right'
    elif _state[2] == 1:
        return 'left'

def outHandle(): #handle out of line by coming where the car moved from, until cleared off the line
    global last_state, current_state
    if last_state == 'left':
        px.set_dir_servo_angle(-30)
        px.backward(10)
    elif last_state == 'right':
        px.set_dir_servo_angle(30)
        px.backward(10)
    while True:
        gm_val_list = px.get_grayscale_data()
        gm_state = get_status(gm_val_list)
        print("outHandle gm_val_list: %s, %s"%(gm_val_list, gm_state))
        currentSta = gm_state
        if currentSta != last_state:
            break
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

            #check for black line
            if gm_state != "stop":
                global last_state 
                last_state = gm_state

            if gm_state == 'forward':
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            elif gm_state == 'left':
                px.set_dir_servo_angle(offset)
                px.forward(POWER)
            elif gm_state == 'right':
                px.set_dir_servo_angle(-offset)
                px.forward(POWER)
            else:
                outHandle()

            #check for distance and avoidance logic
            #sanity check for blind spot
            # px.set_cam_pan_angle(-30)
            # time.sleep(0.5)
            # px.set_cam_pan_angle(0)
            # time.sleep(0.5)
            # px.set_cam_pan_angle(30)

            # print ('entering time monotonic check for cam angle')
            if (elapsed_time%3.0==0):
                px.set_cam_pan_angle(-30)
            elif (elapsed_time%5.0==0):
                px.set_cam_pan_angle(30)
            else:
                px.set_cam_pan_angle(0)

            print ('going into self driving mode')
            if (distance<0):
                # px.forward(0)
                # px.backward(0)
                # sweep_cam_pan_servo(px);
                # temp_new_dir_min_angle=min(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with smallest distance
                # temp_new_dir_max_angle=max(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with largest distance
                # temp_new_dir_min_distance=direction_choices_dictionary[temp_new_dir_min_angle]
                # temp_new_dir_max_distance=direction_choices_dictionary[temp_new_dir_max_angle]
                # print(temp_new_dir_min_angle,temp_new_dir_min_distance)
                # print(temp_new_dir_max_angle,temp_new_dir_max_distance)
                # px.set_dir_servo_angle(temp_new_dir_max_angle)
                # px.forward(POWER)
                # time.sleep(1)
                # px.set_dir_servo_angle(-10) 
                #reading issue, try to wiggle for reading calib
                px.set_cam_pan_angle(-15)
                px.set_cam_pan_angle(0)
                px.set_cam_pan_angle(15)
                px.set_cam_pan_angle(0)
                
            if (no_safe_path_counter>=3):
                print ('no safe path, high possibility of being stuck, call HELP!!!')
                px.set_dir_servo_angle(0)
                px.forward(0)
                return False;
        
            # if distance <0:
            #     print('negative distance dinged')
            #     no_safe_path_counter=0
            #     px.set_cam_pan_angle(0)
            #     px.set_dir_servo_angle(0)
            #     px.forward(POWER)
            #     #sanity check for blind spot
            #     px.set_cam_pan_angle(-30)
            #     if (distance>0):
            #         px.set_dir_servo_angle(-30)
            #         px.forward(POWER)
            #     px.set_cam_pan_angle(30)
            #     if (distance>0):
            #         px.set_dir_servo_angle(30)
            #         px.forward(POWER)
            #     print('negative distance dinged second time')
            # px.set_dir_servo_angle(0)
            # return False
            elif (distance >= SafeDistance and distance>0):
                print('distance >= SafeDistance dinged')
                no_safe_path_counter=0
                px.set_dir_servo_angle(0)
                px.forward(POWER)
                #sanity check for blind spot
                # px.set_cam_pan_angle(-30)
                # time.sleep(0.5)
                # px.set_cam_pan_angle(0)
                # time.sleep(0.5)
                # px.set_cam_pan_angle(30)
            elif (distance >= DangerDistance and distance>0):
                print('distance >= DangerDistance dinged')
                no_safe_path_counter=no_safe_path_counter+1
                px.forward(0)
                time.sleep(1)
                px.backward(POWER)
                time.sleep(1)
                px.backward(0)
                sweep_cam_pan_servo(px);
                temp_new_dir_min_angle=min(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with smallest distance
                temp_new_dir_max_angle=max(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with largest distance
                temp_new_dir_min_distance=direction_choices_dictionary[temp_new_dir_min_angle]
                temp_new_dir_max_distance=direction_choices_dictionary[temp_new_dir_max_angle]
                print(temp_new_dir_min_angle,temp_new_dir_min_distance)
                print(temp_new_dir_max_angle,temp_new_dir_max_distance)
                time.sleep(0.5)
                px.backward(0)
                # if (temp_new_dir_min_value<0):
                #     px.set_dir_servo_angle(temp_new_dir_min)
                # else:
                #     px.set_dir_servo_angle(temp_new_dir_max)
                px.set_dir_servo_angle(temp_new_dir_max_angle)
                px.forward(POWER)
                time.sleep(1) #run forward first for 2 seconds and recheck
                distance = round(px.ultrasonic.read(), 2)
                if (distance > SafeDistance): #if obstacle cleared, move forward 
                    print('distance < SafeDistance dinged, moving forward')
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                    px.forward(POWER)
                    distance = round(px.ultrasonic.read(), 2)
                    # time.sleep(2)
                # time.sleep(2)
                elif (distance < SafeDistance): #if still encounter obstacle, spin another direction to look for more options to go for
                    print('distance < SafeDistance dinged, moving to other direcitons')
                    px.forward(0)
                    time.sleep(1)
                    spin_to_scan(px)
                    no_safe_path_counter=no_safe_path_counter+1
                    distance = round(px.ultrasonic.read(), 2)

            elif (distance < DangerDistance and distance>0):
                print('distance < DangerDistance dinged')
                no_safe_path_counter=no_safe_path_counter+1
                print ('DANGER ZONE!!! BACK UP!!!')
                px.set_dir_servo_angle(0)
                px.backward(0)
                time.sleep(1)
                # px.set_dir_servo_angle(-45)
                px.backward(POWER)
                time.sleep(2)
                px.backward(0)
                #look for a better direction to go to
                distance = float(round(px.ultrasonic.read(), 2))
                print("distance: ",distance)
                sweep_cam_pan_servo(px);
                temp_new_dir_min_angle=min(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with smallest distance
                temp_new_dir_max_angle=max(direction_choices_dictionary, key=direction_choices_dictionary.get) #get angle with largest distance
                temp_new_dir_min_distance=direction_choices_dictionary[temp_new_dir_min_angle]
                temp_new_dir_max_distance=direction_choices_dictionary[temp_new_dir_max_angle]
                print(temp_new_dir_min_angle,temp_new_dir_min_distance)
                print(temp_new_dir_max_angle,temp_new_dir_max_distance)
                time.sleep(0.5)
                px.backward(0)
                # if (temp_new_dir_min_value<0):
                #     px.set_dir_servo_angle(temp_new_dir_min)
                # else:
                #     px.set_dir_servo_angle(temp_new_dir_max)
                px.set_dir_servo_angle(temp_new_dir_max_angle)
                px.forward(POWER)
                time.sleep(1) #run forward first for 1 seconds and recheck
                distance = float(round(px.ultrasonic.read(), 2))
                if (distance > DangerDistance and distance>0): #if obstacle cleared, move forward 
                    print('distance > DangerDistance dinged, moving forward')
                    px.forward(0)
                    px.set_dir_servo_angle(temp_new_dir_max_angle)
                    px.forward(POWER)
                    # time.sleep(2)
                    distance = round(px.ultrasonic.read(), 2)

                # time.sleep(2)
                elif (distance < DangerDistance and distance>0): #if still within danger distance, look for other options to go for
                    print('distance < DangerDistance dinged second time, spinning')
                    spin_to_scan(px)
                    no_safe_path_counter=no_safe_path_counter+1
                    distance = round(px.ultrasonic.read(), 2)

            # elif distance <0:
            #     px.forward(0)
            #     px.set_dir_servo_angle(30)
            #     px.forward(0)
                # return False

    finally:
        px.forward(0)
        if distance <0:
            px.forward(0)
            px.set_dir_servo_angle(0)
            return False


if __name__ == "__main__":
    main()

