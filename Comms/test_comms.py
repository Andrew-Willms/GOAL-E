import serial
import time
import random
import struct

SERIAL_PORT = "/dev/ttyS0" 
BAUD_RATE = 115200 # Ensure the baud rate matches the receiving device
START_MESSAGE_FLAG = 0

try:
    serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f'Serial port {SERIAL_PORT} opened.')
    while True:

        rotation_target: int = random.randint(1, 65535) # 16 bit number
        extension_target: int = random.randint(1, 65535) # 16 bit number
        elevation_target: int = random.randint(1, 65535) # 16 bit number

        # > indicating Big Endian
        # B indicating an unsigned char
        # H indicating an unsigned uint16
        data: bytes = struct.pack('>B>H>H>H', START_MESSAGE_FLAG, rotation_target, extension_target, elevation_target)
        serial_port.write(data)
        print(f"Sent: {rotation_target}, {extension_target}, {elevation_target}")

        for byte_value in data:
            print(byte_value)

        time.sleep(2)

except KeyboardInterrupt:
    print("Exiting program.")
except serial.SerialException as e:
    print(f"Serial error: {e}")
finally:
    if serial_port and serial_port.is_open:
        serial_port.close()
        print("Serial port closed.")