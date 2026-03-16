import comms
import planning
import vision_debug

NEUTRAL_POSITION = (0, 0.5, 1)
DRIFT_TO_NEUTRAL_MAX_VELOCITY = ()

last_target_position: tuple[float, float, float] = (0, 0.5, 1)

while True:

    puck_position: tuple[float, float, float] = vision_debug.get_puck_position()

    if puck_position == None:
        target_position = planning.drift_towards_neutral(last_target_position)
        comms.Send_To_Arduino(target_position)
        continue

    velocity: tuple[float, float, float] = planning.get_velocity()
    goal_plane_intersection: tuple[float, float, float] = planning.goal_plane_intersection(velocity)

    target_position: tuple[float, float, float] = planning.get_target_position()


    comms.Send_To_Arduino(target_position)

