from collections import deque
import numpy as np
import cv2
import imutils
import time

bufferSize = 16

blueIndicate, greenIndicate = False, False

colorRanges = [
        ((29, 86, 6), (64, 255, 255), "Green"),
        ((57, 68, 0), (151, 255, 255), "Blue")]

pts = deque([], maxlen=bufferSize)
pts1 = deque([], maxlen=bufferSize)

counter, counter1 = 0, 0

(dX, dY), (dXB, dYB) = (0, 0), (0, 0)

direction = ""
directionB = ""

vs = cv2.VideoCapture(0)

time.sleep(2.0)

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
        centerGreen, centerBlue = None, None
        # only proceed if at least one contour was found

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            MB = cv2.moments(c)
            centerGreen = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            centerBlue = (int(MB["m10"] / MB["m00"]), int(MB["m01"] / MB["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 30 and colorName == "Green":
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.putText(frame, colorName, centerGreen, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                cv2.circle(frame, centerGreen, 5, (0, 0, 255), -1)
                pts.appendleft(centerGreen)
                if not greenIndicate:
                    greenIndicate = True
                    print("Green Detect = ", greenIndicate)
            elif radius < 30 and colorName == "Green":
                greenIndicate = False
                print("Green Detect = ", greenIndicate)
                pts.appendleft((0, 0))
                
            if radius > 30 and colorName == "Blue":
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
                cv2.putText(frame, colorName, centerBlue, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                cv2.circle(frame, centerBlue, 5, (0, 0, 255), -1)
                pts1.appendleft(centerBlue)
                if not blueIndicate:
                    blueIndicate = True
                    print("Blue Detect = ", blueIndicate)
            elif radius < 30 and colorName == "Blue":
                blueIndicate = False
                print("Blue Detect = ", blueIndicate)
                pts1.appendleft((0, 0))
                # loop over the set of tracked points"""
        for i in np.arange(1, len(pts)):
            # if either of the tracked points are None, ignore them
            if pts[i - 1] is None or pts[i] is None:
                continue

            # check to see if enough points have been accumulated in the buffer
            if counter >= 10 and i == 1 and len(pts) == bufferSize:
                dX = pts[-10][0] - pts[i][0]
                dY = pts[-10][1] - pts[i][1]
                (dirX, dirY) = ("", "")

                if np.abs(dX) > 20:
                    if np.sign(dX) == 1:
                        dirX = "Right"
                    else:
                        dirX = "Left"
                    direction = dirX
                else:
                    direction = dirX if dirX != "" else dirY

            thickness = int(np.sqrt(bufferSize / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

        for i in np.arange(1, len(pts1)):

            if pts1[i - 1] is None or pts1[i] is None:
                continue

            if counter1 >= 10 and i == 1 and len(pts1) == bufferSize:
                dXB = pts1[-10][0] - pts1[i][0]
                dYB = pts1[-10][1] - pts1[i][1]
                (dirXB, dirYB) = ("", "")

                if np.abs(dXB) > 20:
                    if np.sign(dXB) == 1:
                        dirXB = "Right"
                    else:
                        dirXB = "Left"
                    directionB = dirXB

                else:
                    directionB = dirXB if dirXB != "" else dirYB

            thicknessB = int(np.sqrt(bufferSize / float(i + 1)) * 2.5)
            cv2.line(frame, pts1[i - 1], pts1[i], (0, 0, 255), thicknessB)
            
        cv2.putText(frame, directionB, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 3)
        cv2.putText(frame, "dxB: {}, dyB: {}".format(dXB, dYB), (10, frame.shape[0] - 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (255, 0, 0), 1)
            
        cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 3)
        cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                    (0, 0, 255), 1)
    # show the frame to our screen and increment the frame counter
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    counter += 1
    counter1 += 1
    if key == ord("q"):
        break
vs.release()
cv2.destroyAllWindows()
