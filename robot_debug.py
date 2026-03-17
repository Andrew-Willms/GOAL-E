import comms
import planning
import vision_debug
from robot_constants import *



last_target_position: tuple[float, float, float] = NEUTRAL_POSITION

while True:

    puck_position: tuple[float, float, float] = vision_debug.get_puck_position()

    if puck_position == None:
        comms.send_to_arduino(NEUTRAL_POSITION, DRIFT_TO_NEUTRAL_MAX_POWER)
        continue

    target_position: tuple[float, float, float] = planning.get_target_position()
    comms.send_to_arduino(target_position, REGULAR_MAX_POWER)