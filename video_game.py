import keyboard
import time
from robot_constants import *
import comms

rotation: float = 0
extension: float = 0
elevation: float = 0

rotation_change: float = 1
extension_change: float = 0.1

def clamp(number: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(number, maximum))

while True:

    if keyboard.is_pressed('w'):
        extension += extension_change

    if keyboard.is_pressed('a'):
        extension -= extension_change


    if keyboard.is_pressed('w'):
        rotation += rotation_change

    if keyboard.is_pressed('a'):
        rotation -= rotation_change
    

    if keyboard.is_pressed('up'):
        elevation = MAX_ELEVATION

    if keyboard.is_pressed('down'):
        elevation = MIN_ELEVATION
    

    rotation = clamp(rotation, MIN_ROTATION, MAX_ROTATION)
    extension = clamp(extension, MIN_EXTENSION, MAX_EXTENSION)

    comms.send_to_arduino(0, (rotation, extension, elevation), 0)

    # Small delay to prevent the loop from consuming too much CPU
    time.sleep(0.01)

def clamp(number: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(number, maximum))