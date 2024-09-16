from picarx import Picarx
import time

#init for PiCar
px = Picarx()
POWER = 20

#init for distance avoidance
SafeDistance = 25   # > 30 safe
DangerDistance = 10 # > 20 && < 10 backup
direction_choices_dictionary={}

#init for line avoidance
px.set_line_reference([900, 900, 900])
current_state=None
offset=20
last_state='forward'

#Sweeps the camera pan servo from min to max angle with a specific angle stepping and delay
def sweep_cam_pan_servo(self, servo_step=30, delay=1):
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

    #Spin clockwise backward if there is no path ahead after checking
def spin_to_scan(self):
    print ('no safe path ahead, spinning to scan other direction')
   
    self.backward(0)
    time.sleep(1)
    self.set_dir_servo_angle(-30)
    self.backward(20)
    time.sleep(1)

    #check where there is no line
    # [bool, bool, bool], 0 means line, 1 means background and lower than threshold of set_line reference == 1
def get_status(val_list):
    _state = px.get_line_status(val_list)  
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

#handle out of line by coming where the car moved from and back up, until cleared off the line
def outHandle(): 
    print('outHandle triggered')
    global last_state, current_state
    px.forward(0)
    px.backward(0)
    if last_state == 'forward' or current_state=='stop':

        print('forward outhandle triggered')
        px.set_dir_servo_angle(0)
        px.backward(10)
        time.sleep(0.5)

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

    time.sleep(0.001)

#normal handle will try to steer clear and move forward instead of stopping and retreat
def normalHandle(): 
    global last_state, current_state
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
    time.sleep(0.001)



def main():
    try:
        #init all the parameters to default position
        no_safe_path_counter=0
        start_time = time.monotonic()
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
        px.set_dir_servo_angle(0)
        px.set_cam_tilt_angle(0)
        px.set_cam_pan_angle(0)
        distance = round(px.ultrasonic.read(), 2)
        time.sleep(0.5) #ensure sanity check
        global last_state, current_state


        while True:
            #check for time, distance, and grayscale
            end_time = time.monotonic()
            elapsed_time = int(end_time - start_time)
            print("Elapsed time:", elapsed_time, "seconds")
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ",distance)
            #read greyscale/line
            gm_val_list = px.get_grayscale_data()
            gm_state = get_status(gm_val_list)
            print("gm_val_list: %s, %s"%(gm_val_list, gm_state))

            #check for white line, line sensing section
            #grayscale_module (gm_state) check, if it is not under the status stop, go forward,  
            #the the status detect line, it will change the state and this code will try to go to that direction
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


            #distance sensing main section
            #random sanity check for camera angle
            if (elapsed_time%3.0==0):
                px.set_cam_pan_angle(-30)
            elif (elapsed_time%5.0==0):
                px.set_cam_pan_angle(30)
            else:
                px.set_cam_pan_angle(0)

            if (distance<0 or distance<SafeDistance): #sanity check for noises if distance sensed is negative
                px.set_cam_pan_angle(-15)
                px.set_cam_pan_angle(0)
                px.set_cam_pan_angle(15)
                px.set_cam_pan_angle(0)
                distance = round(px.ultrasonic.read(), 2)
            
            #abort and shutdown if retried 3 times
            if (no_safe_path_counter>=3):
                print ('no safe path, high possibility of being stuck, call HELP!!!')
                px.set_dir_servo_angle(0)
                px.forward(0)
                return False;

            #if the distance sensed is larger than safe distance, go forward
            elif (distance >= SafeDistance and distance>0):
                print('distance >= SafeDistance dinged')
                no_safe_path_counter=0
                px.set_dir_servo_angle(0)
                px.forward(POWER)

            #if the distance sensed is smaller than safe distance and entered danger distance, backup immediately, then sweep for safe path
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

                if (temp_new_dir_min_distance<0):
                    px.set_dir_servo_angle(temp_new_dir_min_angle)
                else:
                    px.set_dir_servo_angle(temp_new_dir_max_angle)

                px.forward(POWER+10)
                time.sleep(1) #run forward first for 2 seconds and recheck
                distance = round(px.ultrasonic.read(), 2)
                if (distance > SafeDistance): #if obstacle cleared, move forward 
                    print('distance > SafeDistance dinged, moving forward')
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                    px.forward(POWER)
                    distance = round(px.ultrasonic.read(), 2)

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

                if (temp_new_dir_min_distance<0):
                    px.set_dir_servo_angle(temp_new_dir_min_angle)
                else:
                    px.set_dir_servo_angle(temp_new_dir_max_angle)

                # px.set_dir_servo_angle(temp_new_dir_max_angle)
                px.forward(POWER+10)
                time.sleep(1) #run forward first for 1 seconds and recheck
                distance = float(round(px.ultrasonic.read(), 2))
                if (distance > DangerDistance and distance>0): #if obstacle cleared, move forward 
                    print('distance > DangerDistance dinged, moving forward')
                    px.forward(0)
                    px.set_dir_servo_angle(temp_new_dir_max_angle)
                    px.forward(POWER)

                    distance = round(px.ultrasonic.read(), 2)

                elif (distance < DangerDistance and distance>0): #if still within danger distance, look for other options to go for
                    print('distance < DangerDistance dinged second time, spinning')
                    spin_to_scan(px)
                    no_safe_path_counter=no_safe_path_counter+1
                    distance = round(px.ultrasonic.read(), 2)

    finally:
        #if commanded to stop, stop all motor function
        px.forward(0)
        if distance <0:
            px.forward(0)
            px.set_dir_servo_angle(0)
            return False


if __name__ == "__main__":
    main()