import cv2
import time
from picamera2 import Picamera2

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (2560, 720), "format": "BGR888"},
    #main={"size": (1280, 360), "format": "BGR888"},
    controls={
        "FrameDurationLimits": (11111, 11111)  # 10,638 µs = 94 FPS max
    },
)

picam2.configure(config)
picam2.start()

start_time = time.time()
previous_time = start_time

for i in range(0, 500):

    frame = picam2.capture_array()
    current_time = time.time()
    print(1.0 / (current_time - previous_time))  # FPS

    #cv2.imshow("Frame", frame)

    #if cv2.waitKey(1) == ord('q'):
    #    break

    previous_time = current_time

print(f"average: {500 * 1.0/(time.time() - start_time)}")

cv2.destroyAllWindows()