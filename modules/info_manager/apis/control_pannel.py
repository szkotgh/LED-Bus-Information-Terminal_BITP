import time
import json
import serial
import threading

_SERIAL_PORT = '/dev/ttyUSB0'
_SERIAL_BPS = 115200

arduino = serial.Serial(_SERIAL_PORT, _SERIAL_BPS, timeout=1)

def send_command(command):
    if arduino is None:
        raise Exception("Arduino not connected")
    command = f"{json.dumps(command)}\n"
    arduino.write(command.encode())
    time.sleep(0.05)
    response = arduino.readline().decode().strip()
    return json.loads(response) if response else None

def get_state():
    command = {"command": "GET_ALL"}
    return send_command(command)

def set_states(devices):
    command = {"command": "SET", "variables": devices}
    return send_command(command)