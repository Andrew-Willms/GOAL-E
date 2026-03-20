from camera_constants import *
import cv2
import math
import numpy
from picamera2 import Picamera2
import vision_utilities

FROM_FILE: bool = True



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

# Initialize arrays
lower_bound = numpy.array([127, 65, 27])
upper_bound = numpy.array([152, 255, 255])


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
def get_ball_position() -> tuple[int, int, int, bool] | None:

    global frames_since_big_move

    left_camera_coords: tuple[int, int] | None
    right_camera_coords: tuple[int, int] | None
    (left_camera_coords, right_camera_coords) = get_ball_camera_coords()

    if left_camera_coords == None or right_camera_coords == None:
        return None

    ball_position = get_bal_position(left_camera_coords, right_camera_coords)

    if vision_utilities.point_distance(ball_position, last_ball_position) > LARGE_MOVE_THRESHOLD:
        frames_since_big_move = 0
    else:
        frames_since_big_move += 1

    position_consistent: bool = frames_since_big_move >= POSITION_CONSISTENCY_THRESHOLD

    return (ball_position[0], ball_position[1], ball_position[2], position_consistent)



def get_ball_camera_coords() -> tuple[tuple[int, int] | None, tuple[int, int] | None]:

    frame = picam2.capture_array()
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    left_contours, _ = cv2.findContours(mask[:, :HORIZONTAL_RESOLUTION], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    right_contours, _ = cv2.findContours(mask[:, HORIZONTAL_RESOLUTION:STERO_HORIZONTAL_RESOLUTION], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(left_contours) == 0 or len(right_contours) == 0:
        return (None, None)

    largest_left_contour = max(left_contours, key = cv2.contourArea)
    left_center = vision_utilities.contour_center(largest_left_contour)
    largest_right_contour = max(right_contours, key = cv2.contourArea)
    right_center = vision_utilities.contour_center(largest_right_contour)

    return (left_center, right_center)



def get_bal_position(left_camera_coords: tuple[int, int], right_camera_coords: tuple[int, int]) -> tuple[float, float, float]:

    # positive longitudinal angle points down ice (away from goalie) ??
    # positive lateral angle points to the right

    left_lens_longitudinal_angle: float = math.atan2((left_camera_coords[0] - HORIZONTAL_CENTER) * PIXEL_SIZE, FOCAL_LENGTH)
    left_lens_lateral_angle: float = math.atan2((left_camera_coords[1] - VERITCAL_CENTER) * PIXEL_SIZE, FOCAL_LENGTH)

    right_lens_longitudinal_angle: float = math.atan2(-(right_camera_coords[0] - HORIZONTAL_CENTER) * PIXEL_SIZE, FOCAL_LENGTH)
    right_lens_lateral_angle: float = math.atan2(-(right_camera_coords[1] - VERITCAL_CENTER) * PIXEL_SIZE, FOCAL_LENGTH)

    left_lateral_angle: float = math.pi / 2 - left_lens_lateral_angle - CAMERA_TILT_LEFT
    right_lateral_angle: float = math.pi / 2 + right_lens_lateral_angle - CAMERA_TILT_LEFT
    point_lateral_angle: float = math.pi - left_lateral_angle - right_lateral_angle

    left_camera_distance: float = (INTER_LENS_DISTANCE / math.sin(point_lateral_angle)) * math.sin(right_lateral_angle) # sine law

    average_longitudinal_angle: float = (left_lens_longitudinal_angle + right_lens_longitudinal_angle) / 2
    #if math.fabs(left_lens_longitudinal_angle - right_lens_longitudinal_angle) > math.degrees(5):
    #    print("something fishy, these two should be quite similar")

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

    while True:
        get_ball_position()

    return

if __name__ == "__main__":
    main()