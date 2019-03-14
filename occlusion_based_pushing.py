from collections import deque
import numpy as np
import cv2
import imutils
import time
from gpiozero import Robot
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

bufferSize = 16

OrangeIndicate, GreenIndicate = False, False

colorRanges = [
        ((38, 89, 100), (119, 255, 255), "Green"),
        ((0, 100, 100), (20, 255, 255), "Orange")]

pts = deque([], maxlen=bufferSize)
pts1 = deque([], maxlen=bufferSize)

x_axis, xB_axis = 0, 0

counter, counter1 = 0, 0

(dX, dY), (dXB, dYB) = (0, 0), (0, 0)

direction = ""
directionB = ""

vs = cv2.VideoCapture(0)

time.sleep(2.0)

defaultSpeed = 50
updateSpeed = 25
windowCenter = 300
centerBuffer = 10
pwmBound = float(35)
cameraBound = float(300)
kp = pwmBound / cameraBound
leftBound = int(windowCenter - centerBuffer)
rightBound = int(windowCenter + centerBuffer)
error = 0

# Motor
rightA = 7
rightB = 8
leftA = 10
leftB = 9

GPIO.setup(rightA, GPIO.OUT)
GPIO.setup(rightB, GPIO.OUT)
GPIO.setup(leftA, GPIO.OUT)
GPIO.setup(leftB, GPIO.OUT)

# Disable movements on startup
GPIO.output(rightA, GPIO.LOW)
GPIO.output(rightB, GPIO.LOW)
GPIO.output(leftA, GPIO.LOW)
GPIO.output(leftB, GPIO.LOW)

# PWM Initialization

rightMotorFwd = GPIO.PWM(rightA, defaultSpeed)
leftMotorFwd = GPIO.PWM(leftA, defaultSpeed)
rightMotorRev = GPIO.PWM(rightB, defaultSpeed)
leftMotorRev = GPIO.PWM(leftB, defaultSpeed)

rightMotorFwd.start(defaultSpeed)
leftMotorFwd.start(defaultSpeed)
rightMotorRev.start(defaultSpeed)
leftMotorRev.start(defaultSpeed)

firstScene = 0

def UpdatePwm(right_pwm, left_pwm):
    rightMotorFwd.ChangeDutyCycle(right_pwm)
    leftMotorFwd.ChangeDutyCycle(left_pwm)
    
def UpdatePwmRev(right_pwm, left_pwm):
    GPIO.output(rightA, GPIO.LOW)
    rightMotorRev.ChangeDutyCycle(right_pwm)
    GPIO.output(leftA, GPIO.LOW)
    leftMotorRev.ChangeDutyCycle(left_pwm)
    
def pwmStop():
    rightMotorFwd.ChangeDutyCycle(0)
    rightMotorRev.ChangeDutyCycle(0)
    leftMotorFwd.ChangeDutyCycle(0)
    leftMotorRev.ChangeDutyCycle(0)

while True:
    # grab the current frame
    (grabbed, frame) = vs.read()
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    for (lower, upper, colorName) in colorRanges:
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        centerGreen, centerOrange = None, None
        # only proceed if at least one contour was found

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            MB = cv2.moments(c)
            centerGreen = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            centerOrange = (int(MB["m10"] / MB["m00"]), int(MB["m01"] / MB["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 40 and colorName == "Green":
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.putText(frame, colorName, centerGreen, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                cv2.circle(frame, centerGreen, 5, (0, 0, 255), -1)
                x_axis = int(x)
                pts.appendleft(centerGreen)
                if not GreenIndicate:
                    GreenIndicate = True
                    # print("Green Detect = ", GreenIndicate)
            elif radius < 40:
                GreenIndicate = False
                # print("Green Detect = ", GreenIndicate)

            if radius > 100 and colorName == "Orange":
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
                cv2.putText(frame, colorName, centerOrange, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                cv2.circle(frame, centerOrange, 5, (0, 0, 255), -1)
                xB_axis = int(x)
                pts1.appendleft(centerOrange)
                print(radius)
                if not OrangeIndicate:
                    OrangeIndicate = True
                    # print("Orange Detect = ", OrangeIndicate)
            elif radius < 100:
                OrangeIndicate = False
                print(radius)
                error = 0
                pwmStop()
                # print("Orange Detect = ", OrangeIndicate)
        if firstScene == 0 and OrangeIndicate and GreenIndicate:
            firstScene = firstScene + 1
            if (xB_axis < leftBound) or (xB_axis > rightBound):
                error = windowCenter - xB_axis
                pwmOut = abs(error * kp)
                turnPwm = pwmOut + defaultSpeed
                if xB_axis < (leftBound):
                    if xB_axis < 160:
                        # print(xB_axis)
                        UpdatePwm(defaultSpeed, updateSpeed)
                    else:
                        UpdatePwm(turnPwm, defaultSpeed)
                elif xB_axis > rightBound:
                    if xB_axis > 460:
                        UpdatePwm(updateSpeed, defaultSpeed)
                    else:
                        UpdatePwm(defaultSpeed, turnPwm)
            else:
                UpdatePwm(defaultSpeed, defaultSpeed)
                
        if firstScene == 1 and OrangeIndicate:
            firstScene = 0
            if (xB_axis < leftBound) or (xB_axis > rightBound):
                error = windowCenter - x_axis
                pwmOut = abs(error * kp)
                turnPwm = pwmOut + defaultSpeed
                if xB_axis < (leftBound):
                    if xB_axis < 160:
                        # print(xB_axis)
                        UpdatePwm(defaultSpeed, updateSpeed)
                    else:
                        UpdatePwm(turnPwm, defaultSpeed)
                elif xB_axis > rightBound:
                    if xB_axis > 460:
                        UpdatePwm(updateSpeed, defaultSpeed)
                    else:
                        UpdatePwm(defaultSpeed, turnPwm)
            else:
                UpdatePwm(defaultSpeed, defaultSpeed)
                
        if firstScene == 1 and GreenIndicate:
            firstScene = 0
            if (x_axis < leftBound) or (x_axis > rightBound):
                error = windowCenter - x_axis
                pwmOut = abs(error * kp)
                turnPwm = pwmOut + defaultSpeed
                if x_axis < (leftBound):
                    if x_axis < 160:
                        # print(xB_axis)
                        UpdatePwmRev(defaultSpeed, updateSpeed)
                    else:
                        UpdatePwmRev(turnPwm, defaultSpeed)
                elif x_axis > rightBound:
                    if x_axis > 460:
                        UpdatePwmRev(updateSpeed, defaultSpeed)
                    else:
                        UpdatePwm(defaultSpeed, turnPwm)
            else:
                UpdatePwmRev(defaultSpeed, defaultSpeed)
            
    # show the frame to our screen and increment the frame counter
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(10) & 0xFF
    counter += 1
    counter1 += 1
    if key == ord("q"):
        break
vs.release()
cv2.destroyAllWindows()
GPIO.cleanup()
