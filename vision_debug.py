import cv2
import numpy
import vision_utilities

# Initialize Opencv2 Objects
camera = None
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)
morph_kernel = numpy.ones((5,5), numpy.uint8)

# Color thresholds
lower_bound = numpy.array([138, 57, 190])
upper_bound = numpy.array([177, 255, 255])

# Initialize Sliders
cv2.namedWindow("Mask")
cv2.createTrackbar("minimum hue", "Mask", lower_bound[0], 179, vision_utilities.nothing)
cv2.createTrackbar("maximum hue", "Mask", upper_bound[0], 179, vision_utilities.nothing)
cv2.createTrackbar("minimum saturation", "Mask", lower_bound[1], 255, vision_utilities.nothing)
cv2.createTrackbar("maximum saturation", "Mask", upper_bound[1], 255, vision_utilities.nothing)
cv2.createTrackbar("minimum value", "Mask", lower_bound[2], 255, vision_utilities.nothing)
cv2.createTrackbar("maximum value", "Mask", upper_bound[2], 255, vision_utilities.nothing)

def get_ball_camera_coords() -> tuple[float, float, float] | None:
    return None

# (X, Y, Z)
# When looking down the rink from behind the net
# - X is left to right
# - Y is is up and down (distance from the ground plane)
# - Z is forwards and backwards (down the ice)
def get_puck_position() -> tuple[int, int, int] | None:
    return

def run_cv2() -> bool:

    global lower_bound
    global upper_bound

    lower_bound[0] = cv2.getTrackbarPos("minimum hue", "Mask")
    upper_bound[0] = cv2.getTrackbarPos("maximum hue", "Mask")
    lower_bound[1] = cv2.getTrackbarPos("minimum saturation", "Mask")
    upper_bound[1] = cv2.getTrackbarPos("maximum saturation", "Mask")
    lower_bound[2] = cv2.getTrackbarPos("minimum value", "Mask")
    upper_bound[2] = cv2.getTrackbarPos("maximum value", "Mask")

    successfulRead, frame = camera.read()
    if not successfulRead:
        print("Failed to capture frame")
        return False
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, morph_kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("No ball found")
        return True

    largest_contour = max(contours, key = cv2.contourArea)
    center = vision_utilities.contour_center(largest_contour)
    cv2.circle(mask, center, 5, (0, 0, 255), -1)

    print(center)

    cv2.imshow("Original", frame)
    cv2.imshow("Mask", mask)
    cv2.waitKey(1)

    return True

def main():

    while run_cv2():
        pass

    camera.release()
    cv2.destroyAllWindows()
    return

if __name__ == "__main__":
    main()