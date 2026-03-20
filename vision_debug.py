from camera_constants import *
import cv2
import math
import numpy
from picamera2 import Picamera2
import sys
import threading
import time
import vision_utilities

FROM_FILE: bool = False



# Initialize Cameras
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={
        "size": (FULL_STERO_HORIZONTAL_RESOLUTION, FULL_VERTICAL_RESOLUTION),
        "format": "RGB888"}, # at some point maybe try GRBG (or XBGR8888) and convert later in open cv, see if there is a performance difference
    controls={
        "FrameDurationLimits": (FAME_TIME, FAME_TIME),
    },
)
picam2.configure(config)
picam2.start()

if FROM_FILE:
    video = cv2.VideoCapture('Vision/test_footage - 3.mp4')
    if not video.isOpened:
        print("could not open file")
        sys.exit()

# Initialize arrays
#lower_bound = numpy.array([138, 57, 190])
#upper_bound = numpy.array([177, 255, 255])

# at home
#lower_bound = numpy.array([113, 123, 77])
#upper_bound = numpy.array([137, 255, 255])

# Night Lighting
lower_bound = numpy.array([127, 65, 27])
upper_bound = numpy.array([152, 255, 255])

morph_kernel = numpy.ones((5,5), numpy.uint8)

# Initialize Sliders
cv2.namedWindow("Window")
cv2.setWindowProperty("Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.createTrackbar("minimum hue", "Window", lower_bound[0], 179, vision_utilities.nothing)
cv2.createTrackbar("maximum hue", "Window", upper_bound[0], 179, vision_utilities.nothing)
cv2.createTrackbar("minimum saturation", "Window", lower_bound[1], 255, vision_utilities.nothing)
cv2.createTrackbar("maximum saturation", "Window", upper_bound[1], 255, vision_utilities.nothing)
cv2.createTrackbar("minimum value", "Window", lower_bound[2], 255, vision_utilities.nothing)
cv2.createTrackbar("maximum value", "Window", upper_bound[2], 255, vision_utilities.nothing)

# Threading
latest_frame = None
lock = threading.Lock()

def capture_loop():
    global latest_frame
    while True:
        request = picam2.capture_request()
        frame = request.make_array("main")
        request.release()
        with lock:
            latest_frame = frame

threading.Thread(target=capture_loop, daemon=True).start()



LARGE_MOVE_THRESHOLD: float = 0.18
POSITION_CONSISTENCY_THRESHOLD: int = 30
last_ball_position: tuple[float, float, float] = (0, 0, 0)
frames_since_big_move: int = 100000

# (X, Y, Z)
# When looking down the rink from behind the net
# - X is left and right
#    - X0 is centered on the net
# - Y is is up and down (distance from the ground plane)
#    - Y0 is on the ice
# - Z is forwards and backwards (down the ice)
#    - Z0 is on the outer goal line
def get_ball_position() -> tuple[int, int, int] | None:

    left_camera_coords: tuple[int, int] | None
    right_camera_coords: tuple[int, int] | None
    (left_camera_coords, right_camera_coords) = get_ball_camera_coords()

    if left_camera_coords == None or right_camera_coords == None:
        return None

    print((left_camera_coords, right_camera_coords), end="")

    ball_position = trigonometry(left_camera_coords, right_camera_coords)

    if vision_utilities.point_distance(ball_position, last_ball_position) > LARGE_MOVE_THRESHOLD:
        frames_since_big_move = 0
    else:
        frames_since_big_move += 1

    position_consistent: bool = frames_since_big_move >= POSITION_CONSISTENCY_THRESHOLD

    print(ball_position, end="")
    #print(position_consistent, end="")
    print()
    return (ball_position[0], ball_position[1], ball_position[2], position_consistent)



def get_ball_camera_coords() -> tuple[tuple[int, int] | None, tuple[int, int] | None]:

    global lower_bound
    global upper_bound

    lower_bound[0] = cv2.getTrackbarPos("minimum hue", "Window")
    upper_bound[0] = cv2.getTrackbarPos("maximum hue", "Window")
    lower_bound[1] = cv2.getTrackbarPos("minimum saturation", "Window")
    upper_bound[1] = cv2.getTrackbarPos("maximum saturation", "Window")
    lower_bound[2] = cv2.getTrackbarPos("minimum value", "Window")
    upper_bound[2] = cv2.getTrackbarPos("maximum value", "Window")

    if FROM_FILE:
        success, frame = video.read()
        if not success:
            print("could not read frame")
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return (None, None)     
    else:
        with lock:
            frame = latest_frame.copy() if latest_frame is not None else None
        if frame is None:
            print("latest frame is None")
            return (None, None)

    frame = cv2.resize(frame, (STERO_HORIZONTAL_RESOLUTION, VERTICAL_RESOLUTION))

    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, morph_kernel)

    left_contours, _ = cv2.findContours(mask[:, :HORIZONTAL_RESOLUTION], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    right_contours, _ = cv2.findContours(mask[:, HORIZONTAL_RESOLUTION:STERO_HORIZONTAL_RESOLUTION], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(left_contours) == 0 or len(right_contours) == 0:
        print("no ball found")
        return (None, None)

    largest_left_contour = max(left_contours, key = cv2.contourArea)
    left_center = vision_utilities.contour_center(largest_left_contour)
    largest_right_contour = max(right_contours, key = cv2.contourArea)
    right_center = vision_utilities.contour_center(largest_right_contour)

    # tool slow, trying without
    # Colorize mask, indicate center, combine into a single frame
    #colorized_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    #cv2.circle(colorized_mask, left_center, 5, (0, 0, 255), -1)
    #cv2.circle(colorized_mask, right_center + numpy.array([1280, 0]), 5, (0, 0, 255), -1)
    #combined = numpy.vstack((frame, colorized_mask))
    #cv2.imshow("Window", combined)

    # Iindicate center, draw
    cv2.circle(mask, left_center, 5, (0, 0, 255), -1)
    cv2.circle(mask, right_center + numpy.array([HORIZONTAL_RESOLUTION, 0]), 5, (0, 0, 255), -1)
    cv2.imshow("Window", mask)

    cv2.waitKey(1)
    return (left_center, right_center)



def trigonometry(left_camera_coords: tuple[int, int], right_camera_coords: tuple[int, int]) -> tuple[float, float, float]:

    # positive longitudinal angle points down ice (away from goalie) ??
    # positive lateral angle points to the right

    left_lens_longitudinal_angle: float = math.atan2((left_camera_coords[0] - HORIZONTAL_CENTER) * PIXEL_SIZE, FOCAL_LENGTH)
    left_lens_lateral_angle: float = math.atan2((left_camera_coords[1] - VERITCAL_CENTER) * PIXEL_SIZE, FOCAL_LENGTH)

    right_lens_longitudinal_angle: float = math.atan2(-(right_camera_coords[0] - HORIZONTAL_CENTER) * PIXEL_SIZE, FOCAL_LENGTH)
    right_lens_lateral_angle: float = math.atan2(-(right_camera_coords[1] - VERITCAL_CENTER) * PIXEL_SIZE, FOCAL_LENGTH)

    left_lateral_angle: float = math.pi / 2 - left_lens_lateral_angle - CAMERA_TILT
    right_lateral_angle: float = math.pi / 2 + right_lens_lateral_angle - CAMERA_TILT
    point_lateral_angle: float = math.pi - left_lateral_angle - right_lateral_angle

    print(f"point_lateral_angle {point_lateral_angle}")

    left_camera_distance: float = (INTER_LENS_DISTANCE / math.sin(point_lateral_angle)) * math.sin(right_lateral_angle) # sine law

    print(f"left_camera_distance {left_camera_distance}")

    average_longitudinal_angle: float = (left_lens_longitudinal_angle + right_lens_longitudinal_angle) / 2
    if math.fabs(left_lens_longitudinal_angle - right_lens_longitudinal_angle) > math.degrees(5):
        print("something fishy, these two should be quite similar")

    print(f"average_longitudinal_angle {average_longitudinal_angle}")

    x_from_left_camera: float = math.cos(left_lateral_angle) * left_camera_distance
    yz_hypotenuse_from_left_camera: float = math.sin(left_lateral_angle) * left_camera_distance
    y_from_left_camera: float = -math.cos(average_longitudinal_angle) * yz_hypotenuse_from_left_camera
    z_from_left_camera: float = math.sin(average_longitudinal_angle) * yz_hypotenuse_from_left_camera

    ball_position: tuple[float, float, float] = (
        x_from_left_camera + LEFT_CAMERA_POSITION[0],
        y_from_left_camera + LEFT_CAMERA_POSITION[1],
        z_from_left_camera + LEFT_CAMERA_POSITION[2]
    )

    return ball_position


def main():

    #last_time: float = time.time()

    while True:
        get_ball_position()
        #print(1/(time.time() - last_time))
        #last_time = time.time()

    cv2.destroyAllWindows()
    return

if __name__ == "__main__":
    main()