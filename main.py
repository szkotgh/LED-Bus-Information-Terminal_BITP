import modules.control_manager as control_manager
import modules.matrix_manager as matrix_manager

try:
    import bit_app
    BIT_PROGRAM = bit_app.service
    BIT_PROGRAM.run()
    
except Exception as e:
    control_manager.service.led_control(_error=True)
    notice_repeat = 10
    for i in range(notice_repeat):
        matrix_manager.matrix_pages.text_page(["프로그램에 알 수 없는 오류가 발생했습니다", f"{e}", "", "", "", f"프로그램을 재시작합니다. ({notice_repeat}/{i+1})"], _text_color='red')
    matrix_manager.matrix_pages.exit_page(['오류 발생', '알 수 없는 오류가 발생했습니다.', '', '', 'BIT를 더 이상 실행할 수 없습니다 . . . 프로그램을 재시작합니다.'], 1, 1, 2, _text_color='orange', _status_prt=False, _exit_code=1)