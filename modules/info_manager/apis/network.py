import requests
import socket
import time
import threading
import modules.utils as utils

class NetworkManager:
    def __init__(self, _req_url='http://www.google.com', _default_ip='N/A', _timeout=1):
        self._default_ip = _default_ip
        self._timeout = _timeout
        self._req_url = _req_url
        
        self.wan_ip = self._default_ip
        self.lan_ip = self._default_ip
        
        self.is_internet_connected = False
        self.last_connection_time = None
        
        self.auto_update_thread = None
        self.auto_update_enabled = True
    
    def check_internet_connection(self, _ext_ip: str = '1.1.1.1'):
        # get wan ip
        try:
            ip_response = requests.get('https://api.ipify.org?format=json', timeout=self._timeout)
            self.wan_ip = ip_response.json().get('ip', self._default_ip)
        except Exception as e:
            self.wan_ip = self._default_ip
        
        # get lan ip
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((_ext_ip, 80))
            self.lan_ip = s.getsockname()[0]
            s.close()
        except Exception as e:
            self.lan_ip = self._default_ip
        
        # check internet connection
        try:
            requests.get(self._req_url, timeout=self._timeout)
            self.is_internet_connected = True
        except Exception as e:
            self.is_internet_connected = False
        
        self.last_connection_time = utils.get_now_ftime()
        
        return True
        
    def start_auto_update(self, _interval=1):
        import modules.control_manager as control_manager
        """Start auto update thread"""
        if self.auto_update_thread is not None:
            return False

        def update():
            while True:
                if not self.auto_update_enabled:
                    self.auto_update_thread = None
                    break
                
                self.check_internet_connection()
                
                control_manager.control_pannel.led_control(_internet=self.is_internet_connected)
                
                time.sleep(_interval)

        self.auto_update_enabled = True
        self.auto_update_thread = threading.Thread(target=update, daemon=True)
        self.auto_update_thread.daemon = True
        self.auto_update_thread.start()
        
        return True

    def stop_auto_update(self):
        if self.auto_update_thread is None:
            return False
        self.auto_update_enabled = False
        return True
