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

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)
morph_kernel = numpy.ones((5,5), numpy.uint8)

# Color thresholds
lower_bound = numpy.array([138, 57, 190])
upper_bound = numpy.array([177, 255, 255])

def nothing(x):
    pass

def contour_center(contour) -> tuple[int, int]:

    moments: dict[str, float] = cv2.moments(contour)

    if moments["m00"] == 0:
        return 0, 0

    return int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"])

def run_cv2() -> bool:

    global lower_bound
    global upper_bound

    lower_bound[0] = cv2.getTrackbarPos("minimum hue", "Mask")
    upper_bound[0] = cv2.getTrackbarPos("maximum hue", "Mask")
    lower_bound[1] = cv2.getTrackbarPos("minimum saturation", "Mask")
    upper_bound[1] = cv2.getTrackbarPos("maximum saturation", "Mask")
    lower_bound[2] = cv2.getTrackbarPos("minimum value", "Mask")
    upper_bound[2] = cv2.getTrackbarPos("maximum value", "Mask")

    successfulRead, frame = camera.read()
    if not successfulRead:
        print("Failed to capture frame")
        return False
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

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

    cv2.imshow("Original", frame)
    cv2.imshow("Mask", mask)

    return True

# Initialize Sliders
cv2.namedWindow("Mask")
cv2.createTrackbar("minimum hue", "Mask", lower_bound[0], 179, nothing)
cv2.createTrackbar("maximum hue", "Mask", upper_bound[0], 179, nothing)
cv2.createTrackbar("minimum saturation", "Mask", lower_bound[1], 255, nothing)
cv2.createTrackbar("maximum saturation", "Mask", upper_bound[1], 255, nothing)
cv2.createTrackbar("minimum value", "Mask", lower_bound[2], 255, nothing)
cv2.createTrackbar("maximum value", "Mask", upper_bound[2], 255, nothing)

starting_time_stamp: float = time.time()
frames_processed: int = 0

while run_cv2():
    frames_processed += 1
    cv2.waitKey(1)
    
ending_time_stamp: float = time.time()
frames_per_second: float = (ending_time_stamp - starting_time_stamp) / frames_processed
print("frames per second: {frames_per_second}")

camera.release()
cv2.destroyAllWindows()