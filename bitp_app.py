import os
import sys
import time
import json
import threading
import subprocess

class BITPApp:
    def __init__(self):
        self.OPTION_PATH = os.path.join(os.getcwd(), 'src', 'option.json')
        self.PRCT_INFO_PATH = os.path.join(os.getcwd(), 'src', 'prct_info.json')
        self.ENV_PATH = os.path.join(os.getcwd(), 'src', '.env')
        self.load_modules()
        self.load_options()
        self.load_service_keys()
        self.init_managers()
        self.start_threads()
        self.start_text_print()

    def load_modules(self):
        try:
            import module.utils as utils
            self.utils = utils
        except Exception as e:
            sys.exit(f'module.utils module import failed : {e}')
        try:
            from module.info_manager import InfoManager
            self.InfoManager = InfoManager
        except Exception as e:
            sys.exit(f'module.info_manager module import failed : {e}')
        try:
            from module.matrix_manager import MatrixManager
            self.MatrixManager = MatrixManager
        except Exception as e:
            sys.exit(f'module.matrix_manager module import failed : {e}')
        try:
            from module.speaker_manager import SpeakerManager
            self.SpeakerManager = SpeakerManager
        except Exception as e:
            sys.exit(f'module.speaker_manager module import failed : {e}')

    def load_options(self):
        try:
            with open(self.OPTION_PATH, 'r', encoding='UTF-8') as f:
                self.OPTION = json.loads(f.read())
        except Exception as e:
            sys.exit(f'option.json load failed : {e}')

    def load_service_keys(self):
        self.SERVICE_KEY = self.utils.load_environ(self.ENV_PATH, 'SERVICE_KEY')
        self.GOOGLE_KEY = self.utils.load_environ(self.ENV_PATH, 'GOOGLE_KEY')
        self.SERIAL_KEY = self.utils.load_environ(self.ENV_PATH, 'SERIAL_KEY')
        self.FSERIAL_KEY = '-'.join([self.SERIAL_KEY[i:i+4] for i in range(0, len(self.SERIAL_KEY), 4)])

    def init_managers(self):
        self.speaker_manager = self.SpeakerManager(self.GOOGLE_KEY, self.OPTION)
        self.info_manager = self.InfoManager(self.SERVICE_KEY, self.OPTION)
        self.matrix_manager = self.MatrixManager(self.OPTION, self.speaker_manager)

    def start_threads(self):
        self.thread_list = []
        auto_internet_check_target = threading.Thread(target=self._auto_internet_check_target, daemon=True)
        auto_internet_check_target.start()
        self.thread_list.append(auto_internet_check_target)
        auto_info_update_target = threading.Thread(target=self._auto_info_update_target, daemon=True)
        auto_info_update_target.start()
        self.thread_list.append(auto_info_update_target)

    def _auto_internet_check_target(self, _pr_delay_time:int=5):
        while True:
            self.matrix_manager.network_connected = self.utils.check_internet_connection()
            print(f"[_auto_internet_check_target] internet status: {self.matrix_manager.network_connected}")
            time.sleep(_pr_delay_time)

    def _auto_info_update_target(self, _pr_delay_time:int=30):
        self.info_manager.init_info()
        while True:
            print(f"[_auto_info_update_target] info update started")
            if self.matrix_manager.network_connected:
                self.info_manager.init_arvl_bus_info()
                self.info_manager.init_arvl_bus_info()
                self.info_manager.init_etc_info()
                
                if self.info_manager.is_init and self.info_manager.is_arvl_bus_info_updated and self.info_manager.is_etc_info_updated:
                    self.matrix_manager.update_station_info(self.info_manager.station_datas)
                    print(f"[_auto_info_update_target] matrix_manager info updated")
                else:
                    print(f"[_auto_info_update_target] matrix_manager update canceled. info_manager.is_init: {self.info_manager.is_init}, info_manager.is_arvl_bus_info_updated: {self.info_manager.is_arvl_bus_info_updated}, info_manager.is_etc_info_updated: {self.info_manager.is_etc_info_updated}")
                with open('station_datas_struct.json', 'w', encoding='UTF-8') as f:
                    f.write(json.dumps(self.matrix_manager.station_datas, indent=4))
                print(f"[_auto_info_update_target] info updated")
            else:
                print(f"[_auto_info_update_target] Upload failed: Internet connection has been reported to be poor. Re-update after 5 seconds")
                time.sleep(5)
                continue
            time.sleep(_pr_delay_time)

    def start_text_print(self):
        for i in range(100, -1, -1):
            sec_str = i/10
            if sec_str >= 5:
                sec_str = int(sec_str)
            self.matrix_manager.show_text_page([f"BIT가 시작됩니다 . . . ({sec_str}s)", "", f"{self.utils.get_now_ftime()}", f"IP={self.utils.get_ip()}", f"(v2.1.16) {self.FSERIAL_KEY}"], 0, 0.1, _status_prt=False)

    def show_main_content(self):
        for i in range(0, len(self.info_manager.station_datas)):
            print(f"STATION_DATAS: {i}, {self.info_manager.station_datas[i]}")
            for _repeat in range(0, 3+1):
                self.matrix_manager.show_station_page(i)
            self.matrix_manager.show_station_etc_page(i)