import cv2
import numpy
from picamera2 import Picamera2
import threading
import vision_utilities


# Initialize Cameras
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (2560, 720), "format": "RGB888"}, # at some point maybe try GRBG (or XBGR8888) and convert later in open cv, see if there is a performance difference
    controls={
        "FrameDurationLimits": (11500, 11500),
    },
)
picam2.configure(config)
picam2.start()

# Initialize arrays
lower_bound = numpy.array([138, 57, 190])
upper_bound = numpy.array([177, 255, 255])
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



# (X, Y, Z)
# When looking down the rink from behind the net
# - X is left and right
# - Y is is up and down (distance from the ground plane)
# - Z is forwards and backwards (down the ice)
def get_puck_position() -> tuple[int, int, int] | None:

    ball_camera_coords: tuple[tuple[int, int] | None, tuple[int, int] | None] = get_ball_camera_coords()

    if ball_camera_coords[0] == None or ball_camera_coords[1] == None:
        return None

    return get_bal_position(ball_camera_coords)



def get_ball_camera_coords() -> tuple[tuple[int, int] | None, tuple[int, int] | None]:

    global lower_bound
    global upper_bound

    lower_bound[0] = cv2.getTrackbarPos("minimum hue", "Window")
    upper_bound[0] = cv2.getTrackbarPos("maximum hue", "Window")
    lower_bound[1] = cv2.getTrackbarPos("minimum saturation", "Window")
    upper_bound[1] = cv2.getTrackbarPos("maximum saturation", "Window")
    lower_bound[2] = cv2.getTrackbarPos("minimum value", "Window")
    upper_bound[2] = cv2.getTrackbarPos("maximum value", "Window")

    with lock:
        frame = latest_frame.copy() if latest_frame is not None else None

    if frame is None:
        print("latest frame is None")
        return (None, None)

    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, morph_kernel)

    left_contours, _ = cv2.findContours(mask[:, :1280], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    right_contours, _ = cv2.findContours(mask[:, 1280:2560], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(frame.shape)
    cv2.imshow("left half", hsv[:, :1280])
    cv2.imshow("right half", hsv[:, 1280:2560])

    if len(left_contours) == 0 or len(right_contours) == 0:
        print("no ball found")
        return (None, None)

    largest_left_contour = max(left_contours, key = cv2.contourArea)
    left_center = vision_utilities.contour_center(largest_left_contour)
    largest_right_contour = max(right_contours, key = cv2.contourArea)
    right_center = vision_utilities.contour_center(largest_right_contour)

    # Colorize mask, indicate center, combine into a single frame
    colorized_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    cv2.circle(colorized_mask, left_center, 5, (0, 0, 255), -1)
    cv2.circle(colorized_mask, right_center, 5, (0, 0, 255), -1)
    combined = numpy.vstack((frame, colorized_mask))

    print((left_center, right_center))
    #cv2.imshow("Window", combined)
    cv2.waitKey(1)
    return (left_center, right_center)



def get_bal_position(camera_coords: tuple[tuple[int, int], tuple[int, int]]) -> tuple[float, float, float]:
    return



def main():

    while True:
        get_puck_position()

    cv2.destroyAllWindows()
    return

if __name__ == "__main__":
    main()