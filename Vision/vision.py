import math
from smbus2 import SMBus
import cv2 as cv
import numpy as np
import time
from enum import Enum

# Initialize camera parameters
camera = cv.VideoCapture(0)
camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv.CAP_PROP_FPS, 30)

# Color thresholds
lower_bound = np.array([5, 150, 150])
upper_bound = np.array([20, 255, 255])

def run_cv():

    successfulRead, frame = camera.read()
    if not successfulRead:
        print("Failed to capture frame")
        return
    
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, lower_bound, upper_bound)
    result = cv.bitwise_and(frame, frame, mask=mask)

    # Show windows
    cv.imshow("Original", frame)
    cv.imshow("Orange Mask", mask)
    cv.imshow("Filtered Orange", result)

while True:

    run_cv()

    # Press q to quit
    if cv.waitKey(1) & 0xFF == ord('q'):
        break


camera.release()
cv.destroyAllWindows()