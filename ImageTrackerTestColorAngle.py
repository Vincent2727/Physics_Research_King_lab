# Heavily inspired by https://botforge.wordpress.com/2016/07/20/live-camera-based-angle-calculator-using-python-and-opencv/
#import libs
import cv2
import numpy as np
import math
 
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
 
#filters for orange color and returns orange color position.
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

def calculate_triangle(rframe, rcoords, gcoords, return_initial_pos=False):
    hypotenuse =  distance((gcoords[0],gcoords[1]), (rcoords[0], rcoords[1]))
    #quantifies the horizontal of the triangle
    horizontal = distance((gcoords[0], gcoords[1]), (rcoords[0], gcoords[1]))
    #makes the third-line of the triangle
    thirdline = distance((rcoords[0], rcoords[1]), (rcoords[0], gcoords[1]))
    #calculates the angle using trigonometry
    angle = np.arcsin((thirdline/hypotenuse))* 180/math.pi

    #draws all 3 lines
    cv2.line(rframe, (gcoords[0], gcoords[1]), (rcoords[0], rcoords[1]), (0, 0, 255), 2)
    cv2.line(rframe, (gcoords[0], gcoords[1]), (rcoords[0], gcoords[1]), (0, 0, 255), 2)
    cv2.line(rframe, (rcoords[0], rcoords[1]), (rcoords[0], gcoords[1]), (0,0,255), 2)

        #Allows for calculation until 180 degrees instead of 90
    if rcoords[1] < gcoords[1] and rcoords[0] > gcoords[0]:
        cv2.putText(rframe,str(int(angle)), (20, 20), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,0,0), 2)
    elif rcoords[1] < gcoords[1] and rcoords[0] < gcoords[0]:
        cv2.putText(rframe, str(int(180 - angle)),(20, 20), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,0,0), 2)
    elif rcoords[1] > gcoords[1] and rcoords[0] < gcoords[0]:
        cv2.putText(rframe, str(int(180 + angle)),(20, 20), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,0,0), 2)
    elif rcoords[1] > gcoords[1] and rcoords[0] > gcoords[0]:
        cv2.putText(rframe, str(int(360 - angle)),(20, 20), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,0,0), 2)

    if return_initial_pos:
        cv2.line(rframe, (gcoords[0], gcoords[1]), (rcoords[0], rcoords[1]), (0, 0, 255), 2)

    return hypotenuse, (gcoords[0], gcoords[1]), (rcoords[0], rcoords[1])


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


def diff_tuple(tuple1, tuple2, xy):
    if xy == 0:
        return int(abs(tuple1[0]- tuple2[0]))
    elif xy == 1:
        return int(abs(tuple1[1] - tuple2[1]))


#capture video
cap = cv2.VideoCapture("/Users/vincentdegaetano/Documents/VsCodeProjects/PhysicsResearch/ColorImageTestVid.MOV")


_, frame = cap.read()
(int_grx, int_gry), blogic = findgreen(frame)
(int_rx, int_ry), ologic = findred(frame)

initial_hyp, initial_green, initial_red = calculate_triangle(frame, (int_grx, int_gry), (int_rx, int_ry), return_initial_pos=True)
# Create the initial vector for the line to be drawn on the frame
initial_dx = abs(initial_red[0] - initial_green[0])
initial_dy = initial_red[1] - initial_green[1]

while(1):
    _, frame = cap.read()

    if not _ or frame is None:
        print("Error: Reached end of video or failed to grab frame.")
        break

    fra = frame
     #get coordinates of each object
    (greenx, greeny), blogic = findgreen(fra)
    (redx, redy), rlogic = findred(fra)
    #draw two circles around the objects (you can change the numbers as you like)
    cv2.circle(frame, (greenx, greeny), 20, (0, 255, 0), -1)
    cv2.circle(frame, (redx, redy), 20, (0, 0, 255), -1)

    # draw the initial line with offset
    cv2.line(frame, (greenx, greeny), (greenx - initial_dx, greeny - initial_dy), (0, 0, 0), 2)
    if blogic and rlogic:
    #quantifies the hypotenuse of the triangle
        calculate_triangle(fra, (greenx, greeny), (redx, redy))
        
        # Calculate the angle from the initial vector obtained at the start
        v1 = ((greenx, greeny), (greenx - initial_dx, greeny + initial_dy))
        v2 = ((greenx, greeny), (redx, redy))
        print(dot_angle(v1, v2))


    cv2.imshow("feed", frame)
    cv2.waitKey(0)
    if cv2.waitKey(40) == 27:
        break


cap.release()
cv2.destroyAllWindows()