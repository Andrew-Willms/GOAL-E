
import math



MIN_ROTATION: float = -45
MAX_ROTATION: float = 45

MIN_EXTENSION: float = 0
MAX_EXTENSION: float = 0.6096

MIN_ELEVATION: float = 0
MAX_ELEVATION: float = 0.2667

PIVOT_DEPTH_IN_NET: float = 0.1651

MIN_EXTENSION_THRESHOLD: float = 1
MAX_EXTENSION_THRESHOLD: float = 3
PUCK_DISTANCE_TO_EXTENSION_RATIO: float = MAX_EXTENSION_THRESHOLD / (MAX_EXTENSION_THRESHOLD - MIN_EXTENSION_THRESHOLD)

MIN_ELEVATION_THRESHOLD: float = 0.5
MAX_ELEVATION_THRESHOLD: float = 1
PUCK_HEIGHT_TO_ELEVATION_RATIO: float = MAX_ELEVATION_THRESHOLD / (MAX_ELEVATION_THRESHOLD - MIN_ELEVATION_THRESHOLD)



def get_target_position(puck_position: tuple[float, float, float]) -> tuple[float, float, float]:

    puck_distance_to_pivot: float = puck_position[2] + PIVOT_DEPTH_IN_NET
    puck_angle_from_pivot: float = math.atan2(puck_position[0], puck_distance_to_pivot)

    extension_targate: float = (puck_position[2] - MIN_EXTENSION_THRESHOLD) * PUCK_DISTANCE_TO_EXTENSION_RATIO
    extension_targate = clamp(extension_targate, MIN_EXTENSION, MAX_EXTENSION)

    elevation_target: float = (puck_position[2] - MIN_EXTENSION_THRESHOLD) * PUCK_DISTANCE_TO_EXTENSION_RATIO
    elevation_target = clamp(elevation_target, MIN_ELEVATION, MAX_ELEVATION)

    return (puck_angle_from_pivot, extension_targate, elevation_target)



def clamp(number: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(number, maximum))