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

# Color thresholds
lower_bound = numpy.array([138, 57, 190])
upper_bound = numpy.array([177, 255, 255])

def contour_center(contour) -> tuple[int, int]:

    moments: dict[str, float] = cv2.moments(contour)

    if moments["m00"] == 0:
        return 0, 0

    return int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"])

def run_cv2() -> bool:

    global lower_bound
    global upper_bound

    successfulRead, frame = camera.read()
    if not successfulRead:
        print("Failed to capture frame")
        return False
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    label_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

    if label_count <= 0:
        print("No ball found")
        return True

    largest = 1 + numpy.argmax(stats[1:, cv2.CC_STAT_AREA])
    center = centroids(largest)

    #print(center)

    return True

starting_time_stamp: float = time.time()
frames_processed: int = 0

while run_cv2():
    frames_processed += 1
    
ending_time_stamp: float = time.time()
frames_per_second: float = frames_processed / (ending_time_stamp - starting_time_stamp)
print(f"frames per second: {frames_per_second}")

camera.release()