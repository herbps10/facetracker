# USAGE
# python eyetracking_webcam.py --face cascades/haarcascade_frontalface_default.xml --eye cascades/haarcascade_eye.xml

# import the necessary packages
import sys

from pyimagesearch.eyetracker import EyeTracker
from pyimagesearch import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import time
import cv2
import teensy

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--face", required = True,
	help = "path to where the face cascade resides")
ap.add_argument("-e", "--eyes", required = True,
	help = "path to where the eyes cascade resides")
args = vars(ap.parse_args())

# initialize the camera and grab a reference to the raw camera
# capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# construct the eye tracker and allow the camera to worm up
et = EyeTracker(args["face"], args["eyes"])
time.sleep(0.1)

board = teensy.Teensy("/dev/ttyAMA0", 9600)
board.connect()

x = 75
asc = True
board.motor_absolute(x)


prevcenter = 0
center = 0
found = False


# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image
	frame = f.array

	# resize the frame and convert it to grayscale
	frame = imutils.resize(frame, width = 300)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# detect faces and eyes in the image
	rects = et.track(gray)

	# loop over the face bounding boxes and draw them
	found = False
	for i, rect in enumerate(rects):
		cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)

		found = True
		center = (rect[0] + rect[2]) / 2

	# show the tracked eyes and face, then clear the
	# frame in preparation for the next frame
	cv2.imshow("Tracking", frame)
	rawCapture.truncate(0)

	# if the 'q' key is pressed, stop the loop
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break

	
	if found == True:
		if center > 200:
			x -= 3
		elif center < 100:
			x += 3

		board.motor_absolute(x)

	else:
		if asc == True and x >= 90:
			asc = False
		elif asc == False and x <= 10:
			asc = True

		if asc == True:
			x += 5

		else:
			x -= 5
		
		board.motor_absolute(x)

