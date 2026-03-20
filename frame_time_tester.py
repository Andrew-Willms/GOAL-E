from camera_constants import *
import time
from picamera2 import Picamera2
import vision_utilities

FROM_FILE: bool = True



# Initialize Cameras
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (2560, 720), "format": "RGB888"}, # at some point maybe try GRBG (or XBGR8888) and convert later in open cv, see if there is a performance difference
    controls={
        "FrameDurationLimits": (20000, 20000),
    },
)
picam2.configure(config)
picam2.start()

last_time: float = time.time()
while True:
    frame = picam2.capture_array()
    print(1/(time.time() - last_time))
    last_time = time.time()