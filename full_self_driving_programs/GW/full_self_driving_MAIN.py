from pydoc import text
from vilib import Vilib #adapted and referenced from Sunfounder Vilib library: https://github.com/sunfounder/vilib
from time import sleep, time, strftime, localtime, monotonic_ns
import threading
import readchar
import os
import numpy as np
import a_star_algorithm

#insert here for your own device, controlling the traversal control
from picarx import Picarx


#initialization for PiCarX
px = None
POWER=0
PiCarX_turn=False


#initialization for any other car
###PUT YOUR CODE HERE


#init for utility
#time in nanosecond referencing an absolute clock
start_time = monotonic_ns()
local_map=np.zeros((10,10), dtype=int) 
absolute_map=np.zeros((100, 100), dtype=int)
stop_sleep_time=3 #how many seconds should the car stop for

#init for traffic sign detection with OpenCV and TensorFlow Lite
traffic_sign_detection_bool=False
take_photo_counter=0

def take_photo():
    _time = strftime('%Y-%m-%d-%H-%M-%S',localtime(time()))
    name = 'photo_%s'%_time
    username = os.getlogin()

    path = f"/home/{username}/Pictures/"
    Vilib.take_photo(name, path)
    print('photo save as %s%s.jpg'%(path,name))

def traffic_sign_detection()->bool:
    global take_photo_counter, traffic_sign_detection_bool
    print('traffic sign detection running')
    print ('sanity check on traffic sign type: '+ str(Vilib.detect_obj_parameter['traffic_sign_y']))
    print('traffic sign detection going for if loop')
    if ((Vilib.detect_obj_parameter['traffic_sign_acc']!=None) and (Vilib.detect_obj_parameter['traffic_sign_acc']>0)):
        if (take_photo_counter<1 and take_photo_counter>=0):
            take_photo()
            take_photo_counter=take_photo_counter+1
        traffic_sign_type=Vilib.detect_obj_parameter['traffic_sign_t']
        traffic_sign_coodinate = (Vilib.detect_obj_parameter['traffic_sign_x'],Vilib.detect_obj_parameter['traffic_sign_y'])
        traffic_sign_size = (Vilib.detect_obj_parameter['traffic_sign_w'],Vilib.detect_obj_parameter['traffic_sign_h'])
        print("[traffic_sign Detect] ","Coordinate:",traffic_sign_coodinate,"Size",traffic_sign_size)
        print('traffic sign type is: '+ str(traffic_sign_type))
        print('traffic_sign detected with accuracy: '+str(Vilib.detect_obj_parameter['traffic_sign_acc']))
        traffic_sign_detection_bool=True;
        return True
    else:
        traffic_sign_detection_bool=False
        return False
    
def PicarX_init_func():
    px = Picarx()
    px.set_dir_servo_angle(0)
    px.set_cam_tilt_angle(0)
    px.set_cam_pan_angle(0)
    POWER=30

def PiCarX_STOP_traffic_sign_reaction():
    global POWER
    print('PiCarX_traffic_sign_reaction executed')
    px.forward(0)
    px.backward(0)
    #wait for 3 seconds due to stop sign
    sleep(stop_sleep_time)

    #go until STOP sign cleared
    # while traffic_sign_detection()==True:
    #     px.forward(POWER)
    px.forward(POWER)
    sleep(stop_sleep_time)
    px.forward(0) #sanity check on what to do after
    print('PiCarX_traffic_sign_reaction execution completed, going back to main loop')

def PiCarX_rotate(next_direction='ERROR NEXT DIRECTION'):
    print('PiCarX needs to rotate to: ', next_direction)

def PiCarX_scan():
    print('PiCarX needs to scan!!!')

def main():
    #initialization for main section
    global take_photo_counter, start_time, absolute_map, local_map

    #start video streaming using Rasp Pi as host, transfer with HTTP in localhost, turn traffic_sign_detection to true
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    Vilib.traffic_detect_switch(True)

    #let the hardware warm up for 1 sec
    sleep(1)

    #set coordinate variables for pathfinding
    #placeholder values
    start_coordinate_absolute_map=(0,0)
    stop_coordinate_absolute_map=(99,99)
    start_coordinate_temp_map=(0,0)
    stop_coordinate_temp_map=(10,10)
    current_coordinate=()
    #declaration for next_type data type, not the correct starting value
    next_path=[(-1,-1)]

    #directional init
    current_direction='starting'
    next_direction='starting'

    #detect the distance the car should traverse in specific direction
    length_path=0

    #main loop, for both traffic sign detection and Path finding
    while True:
        print('main full self driving loop running!!!')
        current_time = monotonic_ns()
        time_elapsed=(current_time-start_time)/1000000000
        print ('time elapsed in seconds: ', str(time_elapsed))

        #traffic detection logic
        traffic_sign_detection_bool=traffic_sign_detection()

        #traffic_sign_handling, will be running until traffic_sign_cleared
        if traffic_sign_detection_bool==True:
            # global stop_sleep_time
            print('traffic_sign_detection loop hit!!!')
            PiCarX_STOP_traffic_sign_reaction();

            #car go for 3 blocks
            #adjust for the travel required after the stop sign, drive forward after for 3 secs needs to be counted. 
            #This 3 secs is synced with the stop_sleep_time, thus the out of the order variable name
            length_path-(stop_sleep_time)

            #let the car take a breather
            sleep(1)

        
        if traffic_sign_detection_bool==False:
            # CODE BELOW NOT TESTED YET
            
            if (length_path<=0):
                #make Car turn function required here!!!!!!!
                # local_map=a_star_algorithm.a_star_search_returnMap(absolute_map,start_coordinate_local_map,stop_coordinate_local_map)
                # absolute_map=a_star_algorithm.a_star_search_returnMap(absolute_map,start_coordinate_absolute_map,stop_coordinate_absolute_map)

                # If turning, then recalculate shortest path and length of the specified path, to be feed into the forward control
                if next_direction!='starting':
                    PiCarX_rotate(next_direction);
                
                #always scan and register obstacle in absolute map when length of travel required done
                PiCarX_scan();

                #recalculate the shortest path from the current_coordinate
                next_path=a_star_algorithm.a_star_search_returnPath(absolute_map,current_coordinate,stop_coordinate_absolute_map)
                #grab length required to travel, convert it as to seconds for forward control
                for index, coordinate in next_path:
                    #check for the  difference in first tuple component, if negative = needs to go up; if positive = needs to go down
                    if (next_path[0][index+1][0]-next_path[0][index][0])>0:
                        if (current_direction=='starting' or current_direction=='down'):
                            length_path+=1
                            current_direction='down'
                        else:
                            next_direction='down'
                            stop_coordinate_temp_map=next_path[0][index]
                            break

                    elif (next_path[0][index+1][0]-next_path[0][index][0])<0:
                        if (current_direction=='starting' or current_direction=='up'):
                            length_path+=1
                            current_direction='up'
                        else:
                            next_direction='up'
                            stop_coordinate_temp_map=next_path[0][index]
                            break

                    #check for the  difference in second tuple component, if negative = needs to go right; if positive = needs to go left
                    elif (next_path[0][index+1][1]-next_path[0][index][1])>0:
                        if (current_direction=='starting' or current_direction=='left'):
                            length_path+=1
                            current_direction='left'
                        else:
                            next_direction='left'
                            stop_coordinate_temp_map=next_path[0][index]
                            break

                    elif (next_path[0][index+1][1]-next_path[0][index][1])<0:
                        if (current_direction=='starting' or current_direction=='right'):
                            length_path+=1
                            current_direction='right'
                        else:
                            next_direction='right'
                            stop_coordinate_temp_map=next_path[0][index]
                            break
                    
                    else:
                        print('something is wrong with length measurement!!!')
                        break

            #if Car move forward
            temp_time_driving_anchor=monotonic_ns()
            while ((traffic_sign_detection_bool==False) and ((monotonic_ns()-temp_time_driving_anchor)<length_path)):
                print ('drive the car to the specified desination with directional, length, and power control')
                # this check will break the while loop when the traffic_sign_detected, will go to the main while True loop
                px.forward(POWER)
                traffic_sign_detection_bool=traffic_sign_detection();
                if traffic_sign_detection_bool==True:
                    #update and store remaining length of travel
                    length_path=length_path-(monotonic_ns()-temp_time_driving_anchor)

            #when the drive is cleared as intended from the path, update the current coordinate, and rotate
            if ((monotonic_ns()-temp_time_driving_anchor)>length_path):
                current_coordinate=stop_coordinate_temp_map #track the last coordinate the car should stop at, forward loop, no feedback control loop, careful

            ###YOUR CODE HERE!!!!
            sleep(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print ('exception triggered: ', e)
    finally:
        print("shutting down")
        Vilib.camera_close()
        exit();