import time
import json
import serial
import threading
import modules.matrix_manager as matrix_manager
import modules.config as config
import modules.utils as utils

class ControlPannel:
    def __init__(self, _arduino_port, _arduino_bps):
        self.default_device_states = {'LED1': False, 'LED2': False, 'LED3': False, 'LED4': False, 'RELAY1': True, 'RELAY2': True, 'RELAY3': False, 'RELAY4': False}
        
        try:
            self.arduino = serial.Serial(_arduino_port, _arduino_bps, timeout=0)
            
            success = False
            for i in range(100, 0, -1):
                r = self.get_state()
                matrix_manager.matrix_pages.text_page(f'컨트롤 판넬 연결 중... ({i/10}s)', 0, 0.1, _status_prt=False)
                if r is not None:
                    success = True
                    break
            
            if success:
                matrix_manager.matrix_pages.text_page(['컨트롤 판넬 연결 성공', '초기화 중 . . .'], 0, 0, _text_color='lime', _status_prt=False)
                self.set_states(self.default_device_states)
                matrix_manager.matrix_pages.text_page(['컨트롤 판넬 연결 성공', '실행 중 . . .'], 0, 0, _text_color='lime', _status_prt=False)
                self.button_auto_detect()
                matrix_manager.matrix_pages.text_page(['컨트롤 판넬 연결 성공'], 0, 1, _text_color='lime', _status_prt=False)
            else:
                raise Exception("Control pannel connection failed")
        except Exception as e:
            self.arduino = None
            matrix_manager.matrix_pages.exit_page(['컨트롤 판넬 연결 실패', '컨트롤 판넬에 연결할 수 없습니다.', '', '', 'BIT를 부팅할 수 없습니다 . . . 컨트롤 판넬을 점검하십시오.'], 1, 1, 2, _text_color='orange', _status_prt=False, _exit_code=1)

    def send_command(self, command):
        try:
            if self.arduino is None:
                raise Exception("Arduino not connected")
            command = f"{json.dumps(command)}\n"
            self.arduino.write(command.encode())
            time.sleep(0.05)
            response = self.arduino.readline().decode().strip()
            return json.loads(response) if response else {}
        except:
            return {}

    def get_state(self):
        command = {"command": "GET_ALL"}
        return self.send_command(command)

    def set_states(self, devices):
        command = {"command": "SET", "variables": devices}
        return self.send_command(command)
    
    def init_device(self):
        return self.set_states(self.default_device_states)
    
    def led_control(self, _power: bool = None, _audio: bool = None, _internet: bool = None, _error: bool = None):
        command = {}
        if _power != None:
            command["LED1"] = _power
        if _audio != None:
            command["LED2"] = _audio
        if _internet != None:
            command["LED3"] = _internet
        if _error != None:
            command["LED4"] = _error
        return self.set_states(command)
    
    def fan_control(self, _left: bool = None, _right: bool = None):
        command = {}
        if _left != None:
            command["RELAY1"] = _left
        if _right != None:
            command["RELAY2"] = _right
        return self.set_states(command)
    
    def audio_control(self, _on: bool = None):
        command = {}
        if _on != None:
            command["RELAY3"] = _on
        return self.set_states(command)
    
    def button_auto_detect(self):
        def button_detect():
            previous_button1_state = None
            previous_button2_state = None

            while True:
                try:
                    states = self.get_state()
                    if not states:
                        continue

                    button1_state = states.get('BUTTON1', True)
                    button2_state = states.get('BUTTON2', False)
                    
                    if button1_state != previous_button1_state:
                        self.led_control(_power=button1_state)
                        previous_button1_state = button1_state
                        if button1_state == False:
                            matrix_manager.matrix_pages.exit_page(['BIT를 종료합니다.', '전원버튼이 비활성화 되어있습니다.', '', '', '전원을 재연결해 BIT를 켜십시오.'], 0, 5,  _text_color='orange', _status_prt=False, _exit_code=0)
                        
                    if button2_state != previous_button2_state:
                        self.led_control(_audio=button2_state)
                        self.audio_control(_on=button2_state)
                        previous_button2_state = button2_state
                        
                    time.sleep(config.OPTIONS['control_pannel']['refreshInterval'])
                except Exception as e:
                    time.sleep(1)

        t = threading.Thread(target=button_detect)
        t.daemon = True
        t.start()

service = ControlPannel(_arduino_port=config.OPTIONS['control_pannel']['serialPort'], _arduino_bps=config.OPTIONS['control_pannel']['serialBps'])