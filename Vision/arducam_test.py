import cv2
import time
from picamera2 import Picamera2

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (2560, 720), "format": "YUV420"},
    controls={
        "FrameDurationLimits": (11500, 11500)
    },
)

# 1150 gets 79 fps

picam2.configure(config)
picam2.start()

start_time = time.time()
previous_time = start_time

for i in range(0, 500):

    frame = picam2.capture_array()
    current_time = time.time()
    print(1.0 / (current_time - previous_time))  # FPS
    previous_time = current_time

print(f"average: {500 * 1.0/(time.time() - start_time)}")

cv2.destroyAllWindows()