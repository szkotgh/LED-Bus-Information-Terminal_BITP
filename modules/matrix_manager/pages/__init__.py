
# import modules.matrix_manager.pages.bus_station_page     as bus_station_page
# import modules.matrix_manager.pages.bus_station_etc_page as bus_station_etc_page

class MatrixPages:
    def __init__(self):
        pass
    
    def test_page(self, _test_type: int = 0, _delay_time:int = 1):
        import modules.matrix_manager.pages.test_page as test_page
        try:
            test_page.show_test_page(_test_type, _delay_time)
        except:
            return 1
        return 0
        
    def text_page(self, _set_text: str | list = "", _first_show_time: int | float = 1, _end_show_time: int | float = 1, _repeat: int = 1, _status_prt: bool = True):
        import modules.matrix_manager.pages.text_page as text_page
        try:
            text_page.show_text_page(_set_text, _first_show_time, _end_show_time, _repeat, _status_prt)
        except:
            return 1
        return 0
    
    def everline_page(self, _show_time_sec: int = 15):
        import modules.matrix_manager.pages.everline_page as everline_page
        try:
            everline_page.show_everline_page(_show_time_sec)
        except:
            return 1
        return 0
