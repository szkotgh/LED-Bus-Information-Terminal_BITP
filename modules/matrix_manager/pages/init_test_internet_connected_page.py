import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager
import modules.utils as utils
import modules.config as config

def show_start_page(_show_sec: int = 10, _status_prt: bool = False):
    now_time = utils.get_now_datetime()
    while True:
        # print display
        if info_manager.service.network.is_internet_connected == False:
            matrix_manager.matrix_pages.text_page(
                [
                    f"인터넷과 연결되면 자동으로 부팅됩니다.",
                    f"",
                    f"LAN={info_manager.service.network.lan_ip}",
                    f"WAN={info_manager.service.network.wan_ip}",
                    f"(v{config.VERSION}) {utils.get_now_ftime('%Y-%m-%d %H:%M:%S')}"
                ],
                0, 0.1, _text_color="orange", _status_prt=_status_prt)
        else:
            matrix_manager.matrix_pages.text_page(
                [
                    f"BIT 부팅을 시작합니다 . . .",
                    f"",
                    f"LAN={info_manager.service.network.lan_ip}",
                    f"WAN={info_manager.service.network.wan_ip}",
                    f"(v{config.VERSION}) {utils.get_now_ftime('%Y-%m-%d %H:%M:%S')}"
                ],
                0, 0.1, _text_color="lime", _status_prt=_status_prt)
            
        # show time cal
        if (utils.get_now_datetime() - now_time).total_seconds() >= _show_sec:
            break
    return 0