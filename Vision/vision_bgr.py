import math
import cv2
import numpy
import time
from enum import Enum

# Initialize Opencv2 Objects
camera = cv2.VideoCapture("performance test.mp4")
if not camera.isOpened():
    print("couldn't open video file")
    exit()
morph_kernel = numpy.ones((5,5), numpy.uint8)

# Color thresholds
lower_bound = numpy.array([54, 34, 140])
upper_bound = numpy.array([144, 92, 255])

def nothing(x):
    pass

def contour_center(contour) -> tuple[int, int]:

    moments: dict[str, float] = cv2.moments(contour)

    if moments["m00"] == 0:
        return 0, 0

    return int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"])

last_frame = None
def run_cv2() -> bool:

    global last_frame
    global lower_bound
    global upper_bound

    lower_bound[0] = cv2.getTrackbarPos("minimum B", "Window")
    upper_bound[0] = cv2.getTrackbarPos("maximum B", "Window")
    lower_bound[1] = cv2.getTrackbarPos("minimum G", "Window")
    upper_bound[1] = cv2.getTrackbarPos("maximum G", "Window")
    lower_bound[2] = cv2.getTrackbarPos("minimum R", "Window")
    upper_bound[2] = cv2.getTrackbarPos("maximum R", "Window")

    successfulRead, frame = camera.read()
    if not successfulRead:
        frame = last_frame
    else:
        last_frame = frame
    
    mask = cv2.inRange(frame, lower_bound, upper_bound)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, morph_kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("No ball found")
        return True

    largest_contour = max(contours, key=cv2.contourArea)
    center = contour_center(largest_contour)
    cv2.circle(mask, center, 5, (0, 0, 255), -1)

    print(center)

    colorized_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    combined = numpy.hstack((frame, colorized_mask))

    cv2.imshow("Window", combined)

    return True

# Initialize Sliders
cv2.namedWindow("Window")
cv2.createTrackbar("minimum B", "Window", lower_bound[0], 255, nothing)
cv2.createTrackbar("maximum B", "Window", upper_bound[0], 255, nothing)
cv2.createTrackbar("minimum G", "Window", lower_bound[1], 255, nothing)
cv2.createTrackbar("maximum G", "Window", upper_bound[1], 255, nothing)
cv2.createTrackbar("minimum R", "Window", lower_bound[2], 255, nothing)
cv2.createTrackbar("maximum R", "Window", upper_bound[2], 255, nothing)

while run_cv2():
    cv2.waitKey(1)

camera.release()
cv2.destroyAllWindows()