import comms
import planning
import vision
from robot_constants import *



last_target_position: tuple[float, float, float] = NEUTRAL_POSITION

while True:

    ball_position: tuple[float, float, float, bool] = vision.get_ball_position()

    if ball_position == None:
        comms.send_to_arduino(NEUTRAL_POSITION, DRIFT_TO_NEUTRAL_MAX_POWER)
        continue

    target_position: tuple[float, float, float] = planning.get_target_position((ball_position[0], ball_position[1], ball_position[2]))

    if ball_position[3]:
        comms.send_to_arduino(target_position, REGULAR_MAX_POWER)
    else:
        comms.send_to_arduino(target_position, INCONSISTENT_POSITION_MAX_POWER)