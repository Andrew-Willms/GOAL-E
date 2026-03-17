import cv2
import time
from picamera2 import Picamera2

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (2560, 720), "format": "BGR888"},
    controls={
        "FrameDurationLimits": (100000, 100000)  # 10,638 µs = 94 FPS max
    },
)

picam2.configure(config)
picam2.start()

last_time = time.time()

for i in range(0, 1000):

    frame = picam2.capture_array()
    current_time = time.time()
    print(1.0 / (current_time - last_time))  # FPS

    #cv2.imshow("Frame", frame)

    #if cv2.waitKey(1) == ord('q'):
    #    break

    last_time = current_time

cv2.destroyAllWindows()