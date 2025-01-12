import time
import json
import serial
import threading

SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BPS = 115200

class ControlPannel(threading.Thread):
    def __init__(self, port, bps):
        super().__init__()
        self.port = port
        self.bps = bps
        self.arduino = serial.serial_for_url(self.port, self.bps, timeout=1)
        
        self.status_devices = {'LED1': False, 'LED2': False, 'LED3': False, 'LED4': False, 'BUTTON1': False, 'BUTTON2': False, 'RELAY1': False, 'RELAY2': False, 'RELAY3': False, 'RELAY4': False}
        self.devices_set = {'LED1': False, 'LED2': False, 'LED3': False, 'LED4': False, 'RELAY1': False, 'RELAY2': False, 'RELAY3': False, 'RELAY4': False}
        
        self.auto_refresh_thread = None
        self.auto_refresh_enable = True

    def send_command(self, command):
        command = f"{json.dumps(command)}\n"
        self.arduino.write(command.encode())
        time.sleep(0.05)
        response = self.arduino.readline().decode().strip()
        return json.loads(response) if response else None
    
    def get_state(self):
        command = {"command": "GET_ALL"}
        return self.send_command(command)
    
    def set_states(self, devices):
        command = {"command": "SET", "variables": devices}
        return self.send_command(command)
    
    def auto_refresh(self, _interval_sec:int):
        def refresh():
            while True:
                self.status_devices = self.get_state()
                self.set_states(self.devices_set)
                time.sleep(_interval_sec)
                
                if self.auto_refresh_enable == False:
                    break
        
        self.auto_update_enabled = True
        self.auto_refresh_thread = threading.Thread(target=refresh, daemon=True)
        self.auto_refresh_thread.start()

    def stop_auto_refresh(self):
        if self.auto_refresh_thread is None:
            return False
        self.auto_update_enabled = False
        return True
        
control_pannel = ControlPannel(SERIAL_PORT, SERIAL_BPS)
