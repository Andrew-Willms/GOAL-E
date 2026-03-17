import cv2
import numpy
import time
from picamera2 import Picamera2

# Color thresholds
lower_bound = numpy.array([138, 57, 190])
upper_bound = numpy.array([177, 255, 255])
morph_kernel = numpy.ones((5,5), numpy.uint8)

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (2560, 720), "format": "BGR888"}, # also try "YUV420"
    controls={
        "FrameDurationLimits": (11500, 11500)
    },
)

# 1150 gets 79 fps

picam2.configure(config)
picam2.start()

start_time = time.time()
previous_time = start_time



def contour_center(contour) -> tuple[int, int]:

    moments: dict[str, float] = cv2.moments(contour)

    if moments["m00"] == 0:
        return 0, 0

    return int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"])



for i in range(0, 500):

    frame = picam2.capture_array()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, morph_kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("No ball found")
        continue


    largest_contour = max(contours, key=cv2.contourArea)
    center = contour_center(largest_contour)
    print(center)

    #cv2.circle(mask, center, 5, (0, 0, 255), -1)

    current_time = time.time()
    print(1.0 / (current_time - previous_time))  # FPS
    previous_time = current_time

print(f"average: {500 * 1.0/(time.time() - start_time)}")




