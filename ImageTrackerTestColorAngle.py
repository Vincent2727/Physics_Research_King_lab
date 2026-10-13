# Heavily inspired by https://botforge.wordpress.com/2016/07/20/live-camera-based-angle-calculator-using-python-and-opencv/
#import libs
import cv2
import numpy as np
import math
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from datetime import datetime

# Set the date and time for saving images
timeset = datetime.now()
timeset = timeset.strftime("%H:%M:%S")

#uses distance formula to calculate distance
def distance(tuple1, tuple2):
    dist = math.sqrt((math.fabs(tuple2[0]-tuple1[0]))**2+((math.fabs(tuple2[1]-tuple1[1])))**2)
    return dist
 
#filters for blue color and returns blue color position.
def findgreen(frame):
    maxcontour = None
    green = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    greenlow = np.array([65, 25, 70])#replace with your HSV Values
    greenhi = np.array([85, 70, 135])#replace with your HSV Values
    mask = cv2.inRange(green, greenlow, greenhi)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    cnts= cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    if len(cnts) > 0:
        maxcontour = max(cnts, key = cv2.contourArea)
 
        #All this stuff about moments and M['m10'] etc.. are just to return center coordinates
        M = cv2.moments(maxcontour)
        if M['m00'] > 0 and cv2.contourArea(maxcontour) > 100:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            return (cx, cy), True
        else:
            #(700,700), arbitrary random values that will conveniently not be displayed on screen
            return (700,700), False
    else:
        return (700,700), False
 
#filters for red color and returns red color position.
def findred(frame):
    maxcontour = None
    red = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0,50,50])
    upper_red = np.array([2,255,255])
    mask0 = cv2.inRange(red, lower_red, upper_red)
    # upper mask (170-180)
    lower_red = np.array([177,50,50])
    upper_red = np.array([180,255,255])
    mask1 = cv2.inRange(red, lower_red, upper_red)
    # join my masks
    mask = mask0+mask1  
    res = cv2.bitwise_and(frame, frame, mask=mask)
    cnts, hir = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) > 0:
        maxcontour = max(cnts, key = cv2.contourArea)
        M = cv2.moments(maxcontour)
        if M['m00'] > 0 and cv2.contourArea(maxcontour) > 2000:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            return (cx, cy), True
        else:
            return (700,700), False
    else:
        return (700,700), False

# Function to find the angle between two vectors
def dot_angle(v1, v2):
    # vector form v = ((x0, y0), (x1, y1))
    # Find the magnitude of the vectors
    v1_x = (v1[0][0]- v1[1][0])
    v1_y = (v1[0][1] - v1[1][1])
    v2_x = (v2[0][0]- v2[1][0])
    v2_y = (v2[0][1] - v2[1][1])
    magn_v1 = math.sqrt((v1_x ** 2) + (v1_y ** 2))
    magn_v2 = math.sqrt((v2_x ** 2) + (v2_y ** 2))
    # Find the dot product using the formula cos(theta) = (u.v)/(|u||v|)
    u_dot_v = (v1_x * v2_x) + (v1_y * v2_y)
    cos_theta = u_dot_v / (magn_v1 * magn_v2)
    theta = math.acos(cos_theta)
    return theta * 180/math.pi

# Function to check for which quadrant the angle is in, and return the new angle that has been corrected:
def check_angle(angle, coordr, coordg):
    new_angle = angle
    if coordr[0] > coordg[0] and coordr[1] >= coordg[1]:
        new_angle = 360 - angle
    elif coordr[0] < coordg[0] and coordr[1] >= coordg[1]:
        new_angle = 180 + angle
    elif coordr[0] > coordg[0] and coordr[1] <= coordg[1]:
        new_angle = 180 - angle

    return new_angle

#capture video
cap = cv2.VideoCapture("/Users/vincentdegaetano/Documents/VsCodeProjects/PhysicsResearch/ColorImageTestVid.MOV")
# cap = cv2.VideoCapture("PhysicsResearch/ImageColorTestLong.MOV")

_, frame = cap.read()
(int_grx, int_gry), blogic = findgreen(frame)
(int_rx, int_ry), ologic = findred(frame)

# Create the initial vector for the line to be drawn on the frame
initial_dx = int_rx - int_grx
initial_dy = int_ry - int_gry

# Get the frame rate of the video
fr = cap.get(cv2.CAP_PROP_FPS)
print("\n\n" + str(fr) + "\n\n")

# Find the time per frame
tpf = fr/60

print(f"\n\n {tpf:.2f} \n\n")
# Empty array to save the angle values in
angle_list = []

time_count = [] # Empty list for saving the time assocated with the angle
cur_time = 0
while(1):
    _, frame = cap.read()

    if not _ or frame is None:
        print("Error: No more frames...")
        break

    #get coordinates of each object
    (greenx, greeny), blogic = findgreen(frame)
    (redx, redy), rlogic = findred(frame)

    #draw two circles around the objects
    cv2.circle(frame, (greenx, greeny), 15, (0, 255, 0), -1)
    cv2.circle(frame, (redx, redy), 15, (0, 0, 255), -1)

    # draw the initial line with offset
    cv2.line(frame, (greenx, greeny), (greenx + initial_dx, greeny + initial_dy), (0, 0, 0), 2)
    if blogic and rlogic:


        # Draw the new line for the angle calculation
        cv2.line(frame, (greenx, greeny), (redx, redy), (0, 0, 170), 2)

        # Calculate the angle from the initial vector obtained at the start
        v1 = ((greenx, greeny), (greenx + initial_dx, greeny + initial_dy))
        v2 = ((greenx, greeny), (redx, redy))

        # Find the angle between the two lines
        angle = dot_angle(v1, v2)

        # Append the values to each of the lists
        angle_list.append(angle)
        time_count.append(cur_time)

        # For debugging and manually measuring the angle of each frame:
        print(angle)

    # Update 
    cv2.imshow("feed", frame)
    cur_time += tpf
    cv2.waitKey(0) # When present, this stops the video until any key is pressed
    if cv2.waitKey(40) == 27: # Ends the loop when the escape key is pressed
        break

# Graph the output as angle vs. time
plt.figure(figsize=(20, 10))
plt.plot(time_count, angle_list, color="black", marker='o', markersize=5, markerfacecolor='red')
plt.title('Angle vs Time')
plt.xlabel('Time, s')
plt.ylabel('Angle, degree')
plt.grid(True)
plt.legend()
plt.tight_layout()
name = f'/Users/vincentdegaetano/Documents/VsCodeProjects/PhysicsResearch/Image_Saves/AngleGraph_{timeset}.png'
plt.savefig(name)

cap.release()
cv2.destroyAllWindows()