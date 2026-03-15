import serial
import struct

SERIAL_PORT = "/dev/ttyS0" 
BAUD_RATE = 115200
START_MESSAGE_FLAG = 0

serial_port: serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

def Send_To_Arduino(serial_port: serial, rotation_target: int, extension_target: int, elevation_target: int) -> str:

    # < indicating Little Endian
    # B indicating an unsigned char
    # H indicating an unsigned uint16
    data: bytes = struct.pack("<BHHH", START_MESSAGE_FLAG, rotation_target, extension_target, elevation_target)
    serial_port.write(data)
    print(f"Sent: {rotation_target}, {extension_target}, {elevation_target}")