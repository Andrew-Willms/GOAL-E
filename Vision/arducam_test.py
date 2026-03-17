import cv2
import time
from picamera2 import Picamera2

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (2560, 720), "format": "RGB888"}
)

picam2.configure(config)
picam2.start()

last_time = time.time()

while True:

    frame = picam2.capture_array()
    current_time = time.time()
    print(current_time - last_time)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == ord('q'):
        break

    last_time = current_time

cv2.destroyAllWindows()