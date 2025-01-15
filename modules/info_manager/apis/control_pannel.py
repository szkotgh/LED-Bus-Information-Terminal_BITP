import time
import json
import serial
import modules.matrix_manager as matrix_manager

class ControlPannel:
    def __init__(self, _arduino_port, _arduino_bps):
        self.default_device_states = {'LED1': False, 'LED2': False, 'LED3': False, 'LED4': False, 'RELAY1': False, 'RELAY2': False, 'RELAY3': False, 'RELAY4': False}
        
        try:
            self.arduino = serial.Serial(_arduino_port, _arduino_bps, timeout=0)
            
            success = False
            for i in range(100):
                r = self.get_state()
                matrix_manager.matrix_pages.text_page('컨트롤 판넬 연결 중...', 0, 0.1, _status_prt=False)
                if r is not None:
                    success = True
                    break
            
            if success:
                matrix_manager.matrix_pages.text_page('컨트롤 판넬 연결 성공', 0, 1, _text_color='lime', _status_prt=False)
            else:
                raise Exception("Control pannel connection failed")
        except Exception as e:
            self.arduino = None
            matrix_manager.matrix_pages.exit_page(['컨트롤 판넬 연결 실패', 'BIT를 부팅할 수 없습니다 . . . 컨트롤 판넬을 점검하십시오.'], 1, 1, 2, _status_prt=False)

    def send_command(self, command):
        if self.arduino is None:
            raise Exception("Arduino not connected")
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