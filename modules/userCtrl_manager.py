import time
import json
import serial
import threading

SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BPS = 115200

class SerialHandler(threading.Thread):
    def __init__(self, port, bps):
        super().__init__()
        self.port = port
        self.bps = bps
        self.arduino = serial.serial_for_url(self.port, self.bps, timeout=1)
        self.daemon = True
        self.start()

    def run(self):
        while True:
            if self.arduino is None:
                self.arduino = serial.serial_for_url(self.port, self.bps, timeout=1)
            time.sleep(2)

    def send_command(self, command):
        command = f"{json.dumps(command)}\n"
        self.arduino.write(command.encode())
        time.sleep(0.05)
        response = self.arduino.readline().decode().strip()
        return json.loads(response) if response else None

serial_handler = SerialHandler(SERIAL_PORT, SERIAL_BPS)

def get_state():
    command = {"command": "GET_ALL"}
    return serial_handler.send_command(command)

def set_states(devices):
    command = {"command": "SET", "variables": devices}
    return serial_handler.send_command(command)