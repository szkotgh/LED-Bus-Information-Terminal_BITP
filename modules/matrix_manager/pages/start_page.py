import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager
import modules.utils as utils
import modules.config as config

def show_start_page(_show_sec: int = 10, _status_prt: bool = False):
    for i in range((_show_sec*10)-1, 0, -1):
        sec_str = i/10
        if sec_str >= 5:
            sec_str = int(sec_str)
            
        matrix_manager.matrix_pages.text_page(
            [
                f"BIT 부팅 중. 기다리십시오 . . . ({sec_str}s)",
                f"",
                f"LAN={info_manager.service.network.lan_ip}",
                f"WAN={info_manager.service.network.wan_ip}",
                f"(v{config.VERSION}) {utils.get_now_ftime('%Y-%m-%d %H:%M:%S')}"
            ],
            0, 0.1, _status_prt=_status_prt)