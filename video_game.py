import time
from robot_constants import *
import comms

import sys, tty, termios

def get_single_char_unix():
    #print("Press a key: ", end="", flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd) # Set terminal to raw mode
        ch = sys.stdin.read(1) # Read a single character
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) # Restore terminal settings
    print(ch) # Echo the character
    return ch

# Example usage:
# pressed_char = get_single_char_unix()

rotation: float = 0
extension: float = 0
elevation: float = 0

rotation_change: float = 2
extension_change: float = 0.01

def clamp(number: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(number, maximum))

while True:

    keys = get_single_char_unix()

    if "w" in keys:
        extension += extension_change

    if "a" in keys:
        extension = extension - extension_change


    if "d" in keys:
        rotation += rotation_change

    if "s" in keys:
        rotation = rotation - rotation_change
    

    if "k" in keys:
        elevation = MAX_ELEVATION

    if "m" in keys:
        elevation = MIN_ELEVATION


    if "q" in keys:
        sys.exit()
    

    rotation = clamp(rotation, MIN_ROTATION, MAX_ROTATION)
    extension = clamp(extension, MIN_EXTENSION, MAX_EXTENSION)

    print(rotation)
    print(extension)

    comms.send_to_arduino((rotation, extension, elevation), 0)

    # Small delay to prevent the loop from consuming too much CPU
    time.sleep(0.01)