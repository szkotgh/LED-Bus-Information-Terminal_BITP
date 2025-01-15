class MatrixPages:
    def __init__(self):
        pass
    
    def start_page(self, _show_msec):
        import modules.matrix_manager.pages.start_page as start_page
        start_page.show_start_page(_show_msec)
        return 0
    
    def bus_station_page(self, _station_index: int):
        import modules.matrix_manager.pages.bus_station_page as bus_station_page
        bus_station_page.show_station_page(_station_index, )
        return 0
    
    def bus_station_etc_page(self, _station_index: int, _show_time_sec: int):
        import modules.matrix_manager.pages.bus_station_etc_page as bus_station_etc_page
        bus_station_etc_page.show_station_etc_page(_station_index, _show_time_sec)
        return 0
    
    def test_page(self, _test_type: int = 0, _delay_time:int = 1):
        import modules.matrix_manager.pages.test_page as test_page
        test_page.show_test_page(_test_type, _delay_time)
        return 0
        
    def text_page(self, _set_text: str | list = "", _first_show_time: int | float = 1, _end_show_time: int | float = 1, _repeat: int = 1, _text_color: str = 'white', _status_prt: bool = True):
        import modules.matrix_manager.pages.text_page as text_page
        text_page.show_text_page(_set_text, _first_show_time, _end_show_time, _repeat, _text_color, _status_prt)
        return 0
    
    def exit_page(self, _set_text: str | list = "", _first_show_time: int | float = 1, _end_show_time: int | float = 1, _repeat: int = 1, _text_color: str = 'white', _status_prt: bool = True, _exit_code: int = 1):
        import modules.matrix_manager.pages.text_page as text_page
        text_page.show_text_page(_set_text, _first_show_time, _end_show_time, _repeat, _text_color, _status_prt)
        exit(_exit_code)
    
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