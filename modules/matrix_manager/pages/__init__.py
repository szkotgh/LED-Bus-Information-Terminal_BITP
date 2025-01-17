import os

class MatrixPages:
    def __init__(self):
        pass
    
    def start_page(self, _show_sec: int, _status_prt: bool = False):
        import modules.matrix_manager.pages.start_page as start_page
        start_page.show_start_page(_show_sec, _status_prt)
        return 0
    
    def bus_station_page(self, _show_station_struct):
        import modules.matrix_manager.pages.bus_station_page as bus_station_page
        bus_station_page.show_station_page(_show_station_struct)
        return 0
    
    def bus_station_etc_page(self, _show_station_struct, _show_time_sec: int):
        import modules.matrix_manager.pages.bus_station_etc_page as bus_station_etc_page
        bus_station_etc_page.show_station_etc_page(_show_station_struct, _show_time_sec)
        return 0
    
    def test_page(self, _test_type: int = 0, _delay_time:int = 1):
        import modules.matrix_manager.pages.test_page as test_page
        test_page.show_test_page(_test_type, _delay_time)
        return 0
        
    def text_page(self, _set_text: str | list = "", _first_show_time: int | float = 1, _end_show_time: int | float = 1, _repeat: int = 1, _text_color: str = 'white', _status_prt: bool = True):
        import modules.matrix_manager.pages.text_page as text_page
        text_page.show_text_page(_set_text, _first_show_time, _end_show_time, _repeat, _text_color, _status_prt)
        return 0
    
    def exit_page(self, _set_text: str | list = "", _first_show_time: int | float = 1, _end_show_time: int | float = 1, _repeat: int = 1, _text_color: str = 'white', _status_prt: bool = True, _exit_code: int = 0):
        import modules.matrix_manager.pages.text_page as text_page
        import modules.matrix_manager as matrix_manager
        import modules.control_manager as control_manager
        
        matrix_manager.IS_EXITED = True
        text_page.show_text_page(_set_text, _first_show_time, _end_show_time, _repeat, _text_color, _status_prt, _is_exit_signal=True)
        for i in range(5, 0, -1):
            text_page.show_text_page([f'BIT를 종료합니다.', f'종료 신호를 받았습니다. 종료 코드: {_exit_code}', '', '', f'{i}초 뒤 자동으로 종료됩니다 . . .'], 0, 1, 1, 'white', _status_prt=False, _is_exit_signal=True)
        
        control_manager.control_pannel.init_device()
        self.clear_page()
        
        os._exit(_exit_code)
    
    def clear_page(self):
        import modules.matrix_manager.pages.clear_page as clear_page
        clear_page.show_clear_page()
        return 0
    
    def everline_page(self, _show_time_sec: int = 15):
        import modules.matrix_manager.pages.everline_page as everline_page
        everline_page.show_everline_page(_show_time_sec)
        return 0

    def duk_50th_anniversary_page(self):
        import modules.matrix_manager.pages.duk_50th_anniversary_page as duk_50th_anniversary_page
        duk_50th_anniversary_page.show_duk_50th_anniversary_page()
        return 0