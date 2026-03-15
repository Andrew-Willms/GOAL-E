import serial
import time

SERIAL_PORT = "/dev/ttyS0" 
BAUD_RATE = 115200 # Ensure the baud rate matches the receiving device

try:
    serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f'Serial port {SERIAL_PORT} opened.')
    while True:
        # Send a message
        #message = "Hello RS485 World!\r\n" # Add line breaks for compatibility with some assistants
        message = "a" # Add line breaks for compatibility with some assistants
        #serial_port.write(message.encode())
        serial_port.write(message.encode)
        print(f"Sent: {message.strip()}")
        time.sleep(2) # Send every 2 seconds

except KeyboardInterrupt:
    print("Exiting program.")
except serial.SerialException as e:
    print(f"Serial error: {e}")
finally:
    if serial_port and serial_port.is_open:
        serial_port.close()
        print("Serial port closed.")