import serial
import time
import random

SERIAL_PORT = "/dev/ttyS0" 
BAUD_RATE = 115200 # Ensure the baud rate matches the receiving device

try:
    serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f'Serial port {SERIAL_PORT} opened.')
    while True:

        #start_flag: bytes = int.to_bytes(0, byteorder='big', length=1)
        #serial_port.write(start_flag)

        message: int = random.randint(1, 65535) # 16 bit number
        data: bytes = int.to_bytes(message, byteorder='big', length=3) # send 24 bits, first 8 are the start flag 0
        serial_port.write(data)
        print(f"Sent: {message}")

        time.sleep(2)

except KeyboardInterrupt:
    print("Exiting program.")
except serial.SerialException as e:
    print(f"Serial error: {e}")
finally:
    if serial_port and serial_port.is_open:
        serial_port.close()
        print("Serial port closed.")