import serial
import struct

SERIAL_PORT = "/dev/ttyS0" 
BAUD_RATE = 115200
START_MESSAGE_FLAG = 0

serial_port: serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

def Send_To_Arduino(target_postion: tuple[int, int, int]):

    # < indicating Little Endian
    # B indicating an unsigned char
    # H indicating an unsigned uint16
    data: bytes = struct.pack("<BHHH", START_MESSAGE_FLAG, target_postion[0], target_postion[1], target_postion[2])
    serial_port.write(data)
    print(f"Sent: {target_postion[0]}, {target_postion[1]}, {target_postion[2]}")