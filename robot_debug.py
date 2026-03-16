import comms
import vision_debug

NEUTRAL_POSITION = (0, 0.5, 1)

while True:



    puck_position = vision_debug.get_puck_position()

    if puck_position == None:

    (v_x: float, v_y: float, v_z: float) velocity = get_velocity()

    (rotation_target: int, extension_target: int, elevation_target: int) = get_target_position()


    comms.Send_To_Arduino(serial_port, rotation_target, extension_target, elevation_target)

