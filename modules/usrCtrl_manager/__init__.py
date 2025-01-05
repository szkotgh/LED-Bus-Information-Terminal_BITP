import time
import json
import serial

SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BPS = 115200

arduino = serial.serial_for_url(SERIAL_PORT, SERIAL_BPS, timeout=1)
time.sleep(2)

def send_command(command):
    command = f"{json.dumps(command)}\n"
    print(f"Sending command: {command}", end='')
    arduino.write(command.encode())
    time.sleep(0.05)
    response = arduino.readline().decode().strip()
    return json.loads(response) if response else None

def get_device_state(device):
    command = {"command": "GET", "variable": device}
    return send_command(command)

def get_all_states():
    command = {"command": "GET_ALL"}
    return send_command(command)

def set_device_state(device, state):
    command = {"command": "SET", "variable": device, "state": state}
    return send_command(command)

while True:
    time.sleep(1)
    status = get_all_states()
    if status == None:
        print("Failed to get status")
        continue
    
    set_device_state('LED1', status.get('BUTTON1'))
    set_device_state('LED2', status.get('BUTTON2'))
    if status.get('LED1')==True or status.get('LED2')==True:
        set_device_state('LED3', True)
        set_device_state('LED4', False)
    else:
        set_device_state('LED3', False)
        set_device_state('LED4', True)