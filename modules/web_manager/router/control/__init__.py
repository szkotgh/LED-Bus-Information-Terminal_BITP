from flask import Blueprint, jsonify, render_template, request
import threading
import modules.matrix_manager as matrix_manager

control_bp = Blueprint('control', __name__, url_prefix='/control')

TEST_PASSWORD = "dyhsbit0511**"

@control_bp.route('/')
def index():
    return render_template('control/index.html')

IS_SHUTDOWN = False
@control_bp.route('/shutdown_bit')
def shutdown_bit():
    global IS_SHUTDOWN
    if IS_SHUTDOWN:
        return jsonify({"error": "이미 종료 중입니다."}), 403
    
    password = request.args.get('password')
    
    if password != TEST_PASSWORD:
        return jsonify({"error": "비밀번호가 올바르지 않습니다."}), 403
    
    def shutdown_program():
        matrix_manager.matrix_pages.exit_page(['웹 서버', '종료 명령을 받았습니다.', '', '', '프로그램을 종료합니다 . . .'], 5, 0, _text_color='lime', _status_prt=False, _exit_code=0)
    
    IS_SHUTDOWN = True
    threading.Thread(target=shutdown_program).start()
    return jsonify({"message": "BIT 프로그램을 종료합니다."})

IS_RESTARTING = False
@control_bp.route('/restart_bit')
def restart_bit():
    global IS_RESTARTING
    if IS_RESTARTING:
        return jsonify({"error": "이미 재시작 중입니다."}), 403
    
    password = request.args.get('password')
    
    if password != TEST_PASSWORD:
        return jsonify({"error": "비밀번호가 올바르지 않습니다."}), 403
    
    def restart_program():
        matrix_manager.matrix_pages.exit_page(['웹 서버', '재시작 명령을 받았습니다.', '', '', '프로그램을 재시작합니다 . . .'], 5, 0, _text_color='lime', _status_prt=False, _exit_code=2)
    
    IS_RESTARTING = True
    threading.Thread(target=restart_program).start()
    return jsonify({"message": "BIT 프로그램을 재시작합니다."})