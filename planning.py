
import math
from robot_constants import *



def get_target_position(puck_position: tuple[float, float, float]) -> tuple[float, float, float]:

    puck_distance_to_pivot: float = puck_position[2] + PIVOT_DEPTH_IN_NET
    puck_angle_from_pivot: float = math.degrees(math.atan2(puck_position[0], puck_distance_to_pivot))

    extension_targate: float = (puck_position[2] - MIN_EXTENSION_THRESHOLD) * PUCK_DISTANCE_TO_EXTENSION_RATIO
    extension_targate = clamp(extension_targate, MIN_EXTENSION, MAX_EXTENSION)

    if puck_position[0] < BUTTERFLY_DISTANCE_THRESHOLD and puck_position[1] < BUTTERFLY_HEIGHT_THRESHOLD:
        elevation_target = MIN_ELEVATION
    else:
        elevation_target = MAX_ELEVATION

    elevation_target: float = (puck_position[2] - MIN_EXTENSION_THRESHOLD) * PUCK_DISTANCE_TO_EXTENSION_RATIO
    elevation_target = clamp(elevation_target, MIN_ELEVATION, MAX_ELEVATION)

    return (puck_angle_from_pivot, extension_targate, elevation_target)



def clamp(number: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(number, maximum))