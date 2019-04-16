from collections import deque
import numpy as np
import cv2
import imutils
import time

bufferSize = 16

ObjectIndicate, TargetIndicate = False, False

colorRanges = [
        ((38, 89, 100), (119, 255, 255), "Target"),
        ((0, 100, 100), (20, 255, 255), "Object")]

pts = deque([], maxlen=bufferSize)
pts1 = deque([], maxlen=bufferSize)

x_axis, xB_axis = 0, 0

counter, counter1 = 0, 0

(dX, dY), (dXB, dYB) = (0, 0), (0, 0)

direction = ""
directionB = ""

vs = cv2.VideoCapture(0)

time.sleep(2.0)

Scene = True
while True:
    # grab the current frame
    (grabbed, frame) = vs.read()
    frame = imutils.resize(frame, width=600)
    frame = cv2.flip(frame, 1)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    for (lower, upper, colorName) in colorRanges:
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        centerTarget, centerObject = None, None
        # only proceed if at least one contour was found

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            MB = cv2.moments(c)
            centerTarget = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            centerObject = (int(MB["m10"] / MB["m00"]), int(MB["m01"] / MB["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 80 and colorName == "Target":
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.putText(frame, colorName, centerTarget, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                cv2.circle(frame, centerTarget, 5, (0, 0, 255), -1)
                x_axis = int(x)
                pts.appendleft(centerTarget)
                if not TargetIndicate:
                    TargetIndicate = True
                    # print("Target Detect = ", TargetIndicate)
            elif radius < 100:
                TargetIndicate = False
                # print("Target Detect = ", TargetIndicate)

            if radius > 100 and colorName == "Object":
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
                cv2.putText(frame, colorName, centerObject, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                cv2.circle(frame, centerObject, 5, (0, 0, 255), -1)
                xB_axis = int(x)
                pts1.appendleft(centerObject)
                if not ObjectIndicate:
                    ObjectIndicate = True
                    # print("Object Detect = ", ObjectIndicate)
            elif radius < 100:
                ObjectIndicate = False
                # print("Object Detect = ", ObjectIndicate)
        if TargetIndicate and ObjectIndicate and Scene:
            Scene = False
            if x_axis > xB_axis:
                print(x_axis, ">", xB_axis, "Target Object on the right side")
            if x_axis < xB_axis:
                print(x_axis, "<", xB_axis, "Target Object is on left side")
        if not TargetIndicate and ObjectIndicate and not Scene:
            Scene = True
            print("Totally Occluded")

        for i in np.arange(1, len(pts)):
            # if either of the tracked points are None, ignore them
            if pts[i - 1] is None or pts[i] is None:
                continue

            # check to see if enough points have been accumulated in the buffer
            if counter >= 100 and i == 1 and len(pts) == bufferSize:
                dX = pts[-10][0] - pts[i][0]
                dY = pts[-10][1] - pts[i][1]
                (dirX, dirY) = ("", "")

                if np.abs(dX) > 20:
                    if np.sign(dX) == 1:
                        dirX = "Right"
                    else:
                        dirX = "Left"
                    direction = dirX

            thickness = int(np.sqrt(bufferSize / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
        cv2.putText(frame, direction, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 3)
        cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY), (10, frame.shape[0] - 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)

        for j in np.arange(1, len(pts1)):

            if pts1[j - 1] is None or pts1[j] is None:
                continue

            if counter1 >= 10 and j == 1 and len(pts1) == bufferSize:
                dXB = pts1[-10][0] - pts1[j][0]
                dYB = pts1[-10][1] - pts1[j][1]
                (dirXB, dirYB) = ("", "")

                if np.abs(dXB) > 20:
                    if np.sign(dXB) == 1:
                        dirXB = "Right"
                    else:
                        dirXB = "Left"
                    directionB = dirXB

            thicknessB = int(np.sqrt(bufferSize / float(j + 1)) * 2.5)
            cv2.line(frame, pts1[j - 1], pts1[j], (0, 0, 255), thicknessB)

        cv2.putText(frame, directionB, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 3)
        cv2.putText(frame, "dxB: {}, dyB: {}".format(dXB, dYB), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (255, 0, 0), 1)
    # show the frame to our screen and increment the frame counter
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(10) & 0xFF
    counter += 1
    counter1 += 1
    if key == ord("q"):
        break
vs.release()
cv2.destroyAllWindows()
