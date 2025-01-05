import time
import json
import serial

SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BPS = 115200

arduino = serial.serial_for_url(SERIAL_PORT, SERIAL_BPS, timeout=1)
time.sleep(2)

def set_device_state(device, state):
    command = f"{device} : {'true' if state else 'false'}\n"
    arduino.write(command.encode())
    time.sleep(0.05)

def get_device_state(device):
    command = f"GET : {device}\n"
    arduino.write(command.encode())
    time.sleep(0.05)
    response = arduino.readline().decode().strip()
    return response

def get_all_states():
    command = "GET : ALL\n"
    arduino.write(command.encode())
    time.sleep(0.05)
    response = arduino.readline().decode().strip()
    return response

set_device_state("LED1", True)
print(get_device_state("LED1"))
while True:
    print(get_all_states())
    time.sleep(1)

time.sleep(100)