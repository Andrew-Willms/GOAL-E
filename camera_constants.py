import numpy



FRAME_TIME: int = 25000

FULL_STERO_HORIZONTAL_RESOLUTION: int = 3840
FULL_HORIZONTAL_RESOLUTION: int = 1920
FULL_VERTICAL_RESOLUTION: int = 1200

STERO_HORIZONTAL_RESOLUTION: int = 1920
HORIZONTAL_RESOLUTION: int = 960
VERTICAL_RESOLUTION: int = 600

DEBUG_STERO_HORIZONTAL_RESOLUTION: int = 1920
DEBUG_HORIZONTAL_RESOLUTION: int = 960
DEBUG_VERTICAL_RESOLUTION: int = 600

HORIZONTAL_CENTER: float = HORIZONTAL_RESOLUTION / 2 - 0.5
VERITCAL_CENTER: float = VERTICAL_RESOLUTION / 2 - 0.5

DEBUG_HORIZONTAL_CENTER: float = DEBUG_HORIZONTAL_RESOLUTION / 2 - 0.5
DEBUG_VERITCAL_CENTER: float = DEBUG_VERTICAL_RESOLUTION / 2 - 0.5

FOCAL_LENGTH: float = 1.8 # mm # 3.6, the specs say 3.6 but it's definitely half that
PIXEL_SIZE: float = 0.003 # mm

CAMERA_TILT_RIGHT: float = 0.0650414399 # rad, #cad: 0.05323254,
CAMERA_TILT_LEFT: float = 0.06362923658554 # left lens: 0.06362923658554
#INTER_LENS_DISTANCE: float = 0.3271774 # m, planned
#INTER_LENS_DISTANCE: float = 0.3045 # m, actual
INTER_LENS_DISTANCE: float = 0.3445 # m, test footage


LEFT_CAMERA_POSITION: tuple[float, float, float] = (-0.15225, 2.082, 1.7328007) # m

# Pink at Night
lower_bound = numpy.array([127, 65, 27])
upper_bound = numpy.array([152, 255, 255])

# Green During the Day
#lower_bound = numpy.array([43, 64, 60])
#upper_bound = numpy.array([62, 255, 255])

MORPH_KERNEL = numpy.ones((5,5), numpy.uint8)

MINIMUM_CONTOUR_AREA = 150 # pixels

LARGE_MOVE_THRESHOLD: float = 0.18 # m
POSITION_CONSISTENCY_THRESHOLD: int = 30 # frame count