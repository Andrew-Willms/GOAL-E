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
#lower_bound = np.array([5, 150, 150])
#upper_bound = np.array([127, 255, 255])

def nothing(x):
    pass

def contour_center(contour) -> tuple[int, int]:

    moments: dict[str, float] = cv.moments(contour)

    if moments["m00"]:
        return 0, 0

    return int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"])

def run_cv():

    minimum_hue = cv.getTrackbarPos("minimum hue", "Mask")
    maximum_hue = cv.getTrackbarPos("maximum hue", "Mask")
    minimum_saturation = cv.getTrackbarPos("minimum saturation", "Mask")
    maximum_saturation = cv.getTrackbarPos("maximum saturation", "Mask")
    minimum_value = cv.getTrackbarPos("minimum value", "Mask")
    maximum_value = cv.getTrackbarPos("maximum value", "Mask")

    lower_bound = np.array([minimum_hue, minimum_saturation, minimum_value])
    upper_bound = np.array([maximum_hue, maximum_saturation, maximum_value])

    successfulRead, frame = camera.read()
    if not successfulRead:
        print("Failed to capture frame")
        return
    
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, lower_bound, upper_bound)

    kernel = np.ones((5,5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    largest_contour = max(contours, key=cv.contourArea)
    if largest_contour == None:
        print("No ball found")
        return

    center = contour_center(largest_contour)
    cv.circle(mask, center, 2, (0, 0, 255), -1)

    # Show windows
    cv.imshow("Original", frame)
    cv.imshow("Mask", mask)

minimum_hue: int = 138
maximum_hue: int = 177
minimum_saturation: int = 57
maximum_saturation: int = 255
minimum_value: int = 190
maximum_value: int = 255

cv.namedWindow("Mask")
cv.createTrackbar("minimum hue", "Mask", minimum_hue, 179, nothing)
cv.createTrackbar("maximum hue", "Mask", maximum_hue, 179, nothing)
cv.createTrackbar("minimum saturation", "Mask", minimum_saturation, 255, nothing)
cv.createTrackbar("maximum saturation", "Mask", maximum_saturation, 255, nothing)
cv.createTrackbar("minimum value", "Mask", minimum_value, 255, nothing)
cv.createTrackbar("maximum value", "Mask", maximum_value, 255, nothing)

while True:

    run_cv()

    # Press q to quit
    if cv.waitKey(1) & 0xFF == ord('q'):
        break


camera.release()
cv.destroyAllWindows()