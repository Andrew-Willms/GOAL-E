import serial
import struct



SERIAL_PORT: str = "/dev/ttyAMA0" 
BAUD_RATE: int = 115200
START_MESSAGE_FLAG: int = 0

serial_port: serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)



def send_to_arduino(target_postion: tuple[float, float, float], max_power: int):

    # < indicating Little Endian
    # B indicating an unsigned char
    # H indicating an unsigned uint16
    data: bytes = struct.pack("<BBfff", START_MESSAGE_FLAG, max_power, target_postion[0], target_postion[1], target_postion[2])
    serial_port.write(data)
    #print(f"Sent: {max_power}, {target_postion[0]}, {target_postion[1]}, {target_postion[2]}")