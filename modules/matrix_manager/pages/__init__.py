class MatrixPages:
    def __init__(self):
        pass
    
    def test_page(self, _test_type: int = 0, _delay_time:int = 1):
        import modules.matrix_manager.pages.test_page as test_page
        test_page.show_test_page(_test_type, _delay_time)
        return 0
        
    def text_page(self, _set_text: str | list = "", _first_show_time: int | float = 1, _end_show_time: int | float = 1, _repeat: int = 1, _status_prt: bool = True):
        import modules.matrix_manager.pages.text_page as text_page
        text_page.show_text_page(_set_text, _first_show_time, _end_show_time, _repeat, _status_prt)
        return 0
    
    def clear_page(self):
        import modules.matrix_manager.pages.clear_page as clear_page
        clear_page.show_clear_page()
        return 0
    
    def everline_page(self, _show_time_sec: int = 15):
        import modules.matrix_manager.pages.everline_page as everline_page
        everline_page.show_everline_page(_show_time_sec)
        return 0
