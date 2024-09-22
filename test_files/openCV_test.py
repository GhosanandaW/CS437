import cv2
import os
# assign directory
directory = '/dev/'
 
# iterate over files in
# that directory
# for filename in os.listdir(directory):
    # f = os.path.join(directory, filename)
    # # checking if it is a file
    # if os.path.isfile(f):
    #     print(f)

cap = cv2.VideoCapture(19)
ret, frame = cap.read()
print (ret,frame)
# print (cap)
# print(ret, frame)
# for iter in range (36):
#     cap = cv2.VideoCapture(1)
#     ret, frame = cap.read()
#     print (cap)
#     print(ret, frame)