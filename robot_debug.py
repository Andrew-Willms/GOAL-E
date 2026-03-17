import comms
import planning
import vision_debug

NEUTRAL_POSITION: tuple[float, float, float] = (0, 0.5, 1) # (rotation, extension, elevation)
DRIFT_TO_NEUTRAL_MAX_POWER: int = 63
REGULAR_MAX_POWER: int = 255

last_target_position: tuple[float, float, float] = (0, 0.5, 1)

while True:

    puck_position: tuple[float, float, float] = vision_debug.get_puck_position()

    if puck_position == None:
        comms.send_to_arduino(NEUTRAL_POSITION, DRIFT_TO_NEUTRAL_MAX_POWER)
        continue

    target_position: tuple[float, float, float] = planning.get_target_position()


    comms.Send_To_Arduino(target_position)

