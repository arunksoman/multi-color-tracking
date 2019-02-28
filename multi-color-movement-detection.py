# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32, help="max buffer size")
args = vars(ap.parse_args())

apB = argparse.ArgumentParser()
apB.add_argument("-v", "--video", help="path to the (optional) video file")
apB.add_argument("-b", "--bufferB", type=int, default=32, help="max buffer size")
argsB = vars(apB.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space
colorRanges = [
        ((29, 86, 6), (64, 255,255), "Green"),
        ((57, 68,0), (151, 255, 255), "Blue")]

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
pts1 = deque(maxlen=argsB["bufferB"])
counter = 0
counter1 = 0
(dX, dY) = (0, 0)
(dXB, dYB) = (0, 0)
direction = ""
directionB = ""

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
    # grab the current frame
    frame = vs.read()

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    for (lower, upper, colorName) in colorRanges:
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        centerGreen = None
        centerBlue = None
        # only proceed if at least one contour was found
	
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            MB = cv2.moments(c)
            centerGreen = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            centerBlue = (int(MB["m10"] / MB["m00"]), int(MB["m01"] / MB["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10 and colorName == "Green":
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.putText(frame, colorName, centerGreen, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                cv2.circle(frame, centerGreen, 5, (0, 0, 255), -1)
                pts.appendleft(centerGreen)
                
            if radius > 10 and colorName == "Blue":
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
                cv2.putText(frame, colorName, centerBlue, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                cv2.circle(frame, centerBlue, 5, (0, 0, 255), -1)
                pts1.appendleft(centerBlue)
                # loop over the set of tracked points"""
        for i in np.arange(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue

            # check to see if enough points have been accumulated in
            # the buffer
            if counter >= 10 and i == 1 and len(pts) == args["buffer"]:
                # compute the difference between the x and y
                # coordinates and re-initialize the direction
                # text variables
                dX = pts[-10][0] - pts[i][0]
                dY = pts[-10][1] - pts[i][1]
                (dirX, dirY) = ("", "")

                # ensure there is significant movement in the
                # x-direction
                if np.abs(dX) > 20:
                    dirX = "Right" if np.sign(dX) == 1 else "Left"

                # ensure there is significant movement in the
                # y-direction
                if np.abs(dY) > 20:
                    dirY = "Top" if np.sign(dY) == 1 else "Bottom"

                # handle when both directions are non-empty
                if dirX != "" and dirY != "":
                    direction = "{}-{}".format(dirY, dirX)

                # otherwise, only one direction is non-empty
                else:
                    direction = dirX if dirX != "" else dirY

            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
            
            
            
            
        for i in np.arange(1, len(pts1)):
            # if either of the tracked points are None, ignore
            # them
            if pts1[i - 1] is None or pts1[i] is None:
                continue

            # check to see if enough points have been accumulated in
            # the buffer
            if counter1 >= 10 and i == 1 and len(pts1) == argsB["bufferB"]:
                # compute the difference between the x and y
                # coordinates and re-initialize the direction
                # text variables
                dXB = pts1[-10][0] - pts1[i][0]
                dYB= pts1[-10][1] - pts1[i][1]
                (dirXB, dirYB) = ("", "")

                # ensure there is significant movement in the
                # x-direction
                if np.abs(dXB) > 20:
                    dirXB = "Right" if np.sign(dXB) == 1 else "Left"

                # ensure there is significant movement in the
                # y-direction
                if np.abs(dYB) > 20:
                    dirYB = "Top" if np.sign(dYB) == 1 else "Bottom"

                # handle when both directions are non-empty
                if dirXB != "" and dirYB != "":
                    directionB = "{}-{}".format(dirYB, dirXB)

                # otherwise, only one direction is non-empty
                else:
                    directionB = dirXB if dirXB != "" else dirYB

            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thicknessB = int(np.sqrt(argsB["bufferB"] / float(i + 1)) * 2.5)
            cv2.line(frame, pts1[i - 1], pts1[i], (0, 0, 255), thicknessB)

        # show the movement deltas and the direction of movement on
        # the frame
            
        cv2.putText(frame, directionB, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 3)
        cv2.putText(frame, "dxB: {}, dyB: {}".format(dXB, dYB), (10, frame.shape[0] - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 0), 1)
            
            
            

        # show the movement deltas and the direction of movement on
        # the frame
            
        cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 3)
        cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            

    # show the frame to our screen and increment the frame counter
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    counter += 1
    counter1 += 1

        # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()

# otherwise, release the camera
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()
