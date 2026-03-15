import serial
import time
import random
import struct
import Comms



while True:



    (x: float, y: float, z: float) position = vision()

    (v_x: float, v_y: float, v_z: float) velocity = get_velocity()

    (rotation_target: int, extension_target: int, elevation_target: int) = get_target_position()


    Comms.Send_To_Arduino(serial_port, rotation_target, extension_target, elevation_target)

