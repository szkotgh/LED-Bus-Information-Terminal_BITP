import os
import datetime
import socket
import secrets
import re
from flask import Flask, request, render_template, session, redirect, url_for, flash, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv, set_key, find_dotenv

load_dotenv()

# Configuration
SERVER_IP = 'localhost'
SERVER_PORT = 80
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = ['mp4', 'wmv', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif', 'txt']
LOG_FILE = os.path.join(os.getcwd(), 'log', 'bit-web-server.log')
MAX_STORAGE = 1024 * 1024 * 1024 * 1.5  # 1.5GB

# Helper functions
def get_now_ftime() -> str:
    now = datetime.datetime.now()
    return now.isoformat()

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_env(key: str, value: str):
    env_path = find_dotenv()
    set_key(env_path, key, value)
    load_dotenv(override=True)

def get_client_ip(request) -> str:
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

def log_message(content: str, write_for_server: bool | None = False):
    def format_log_message(content: str) -> str:
        return f"{get_now_ftime()} [{get_client_ip(request)}] : {content}"
    
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))
    
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        if write_for_server:
            log_file.write('\n' + f"{get_now_ftime()} SERVER : {content}")
        else:
            log_file.write('\n' + format_log_message(content))

def calculate_storage_usage():
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(UPLOAD_FOLDER):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} ?B"

def get_usage_percentage(used, total):
    use_per = (used / total) * 100
    return f"{use_per:.2f}"

# Flask app initialization
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secrets.token_hex(32)

# Routes
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        if not session.get('logged_in'):
            flash('로그인 후 접속하세요.')
            log_message('관리페이지 접속 실패: 로그인 상태가 아님.')
            return redirect(url_for('login'))
        
        with open(LOG_FILE, 'r', encoding='utf-8') as log_file:
            logs = log_file.read()
        extensions = ', '.join(ALLOWED_EXTENSIONS)
        
        files = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
        
        total_used = calculate_storage_usage()
        formatted_total_used = format_size(total_used)
        formatted_max_storage = format_size(MAX_STORAGE)
        usage_percentage = get_usage_percentage(total_used, MAX_STORAGE)
        return render_template('index.html', my_ip=get_client_ip(request), logs=logs, files=files, extensions=extensions,
                               total_used=formatted_total_used, max_storage=formatted_max_storage,
                               usage_percentage=usage_percentage)
    
    if request.method == 'POST':
        if not session.get('logged_in'):
            flash('로그인 후 작업하세요.')
            log_message('업로드 실패: 로그인 상태가 아님.')
            return redirect(url_for('login'))
        
        file = request.files.get('savefile')
        if not file or file.filename == '':
            log_message('업로드 실패: 파일을 선택하세요.')
            session['upload_status'] = '업로드 실패: 파일을 선택하세요.'
            return redirect(url_for('main'))

        filename = secure_filename(file.filename)
        file_size = len(file.read())
        file.seek(0)
        
        total_used = calculate_storage_usage()
        if total_used + file_size > MAX_STORAGE:
            log_message(f'업로드 실패: 최대 저장 용량 초과. ({filename})')
            session['upload_status'] = f'업로드 실패: 최대 저장 용량 초과. ({filename})'
            return redirect(url_for('main'))
        
        if not allowed_file(filename):
            log_message(f'업로드 실패: 지원되지 않는 확장자입니다. ({filename})')
            session['upload_status'] = f'업로드 실패: 지원되지 않는 확장자입니다. ({filename})'
            return redirect(url_for('main'))

        file_pattern = r'^[a-zA-Z0-9\W_]{1,128}$'
        if not re.match(file_pattern, filename):
            log_message(f'업로드 실패: 파일명이 올바르지 않습니다. ({filename})')
            session['upload_status'] = f'업로드 실패: 파일명이 올바르지 않습니다. 파일명을 줄인 후 다시 시도하세요. ({filename})'
            return redirect(url_for('main'))
        
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            filename = f"{base}_{counter}{ext}"
            counter += 1

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        log_message(f'업로드 성공. ({filename})')
        session['upload_status'] = f'업로드 성공. ({filename})'
        
        return redirect(url_for('main'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('logged_in'):
            return redirect(url_for('main'))

        return render_template('login.html')
    
    if request.method == 'POST':
        _input_id = request.form['username']
        _input_pw = request.form['password']
        
        if judg_admin_credentials(_input_id, _input_pw):
            session['logged_in'] = True
            log_message('로그인 성공.')
            flash('로그인 성공.', 'success')
            
            return redirect(url_for('main'))
        else:
            log_message(f'로그인 실패. id({_input_id})pw({_input_pw})')
            flash('로그인 실패. 관리자 정보가 올바르지 않음.', 'danger')
        
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    if session.pop('logged_in', None):
        log_message(f'로그아웃 됨.')
    return redirect(url_for('login'))

@app.route('/admin_settings', methods=['GET', 'POST'])
def admin_settings():
    id_pattern = r'^[a-zA-Z0-9\W_]{4,64}$'
    pw_pattern = r'^[a-zA-Z0-9\W_]{8,256}$'
    
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message('관리자 정보 변경 실패: 로그인 상태가 아님.')
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template('admin_settings.html')
    
    if request.method == 'POST':
        _new_id = request.form['id']
        _new_pw = request.form['pw']
        _old_id = request.form['old-id']
        _old_pw = request.form['old-pw']
        
        if not (_new_id and _new_pw):
            log_message('관리자 정보 변경 실패: 입력값 오류.')
            return redirect(url_for('main'))
        
        if judg_admin_credentials(_old_id, _old_pw) == False:
            log_message('관리자 정보 변경 실패: 기존 ID 또는 PW 입력 오류.')
            return redirect(url_for('main'))
        
        if not re.match(id_pattern, _new_id) or not re.match(pw_pattern, _new_pw):
            log_message('관리자 정보 변경 실패: 변경할 ID 또는 PW 입력 오류.')
            return redirect(url_for('main'))
        
        new_username_hash = generate_password_hash(_new_id)
        new_password_hash = generate_password_hash(_new_pw)
        update_env('ADMIN_ID', new_username_hash)
        update_env('ADMIN_PW', new_password_hash)
        
        app.secret_key = secrets.token_hex(32)
        
        log_message('관리자 정보 변경 성공. 모든 세션 로그아웃 성공.')
        flash('관리자 정보가 성공적으로 변경되었으며, 모든 세션이 로그아웃되었습니다.', 'success')
        
        return redirect(url_for('login'))

@app.route('/view/<string:filename>')
def view(filename):
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        return redirect(url_for('login'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    else:
        return redirect(url_for('main'))

@app.route('/download/<string:filename>')
def download_file(filename):
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        return redirect(url_for('login'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        log_message(f'다운로드 성공. ({filename})')
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    else:
        log_message(f'다운로드 실패: 파일이 없음. ({filename})')
        return render_template('404_not_found.html'), 404

@app.route('/delete_file', methods=['POST'])
def delete_file():
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message(f'파일 삭제 실패: 로그인 상태가 아님. ({request.form["filename"]})')
        return redirect(url_for('login')), 403

    try:
        filename = request.form['filename']
    except KeyError:
        return redirect(url_for('main')), 400
    
    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    if not file_path.startswith(app.config['UPLOAD_FOLDER']):
        log_message(f'파일 삭제 실패: 잘못된 경로 시도. ({safe_filename})')
        return redirect(url_for('main')), 400

    if os.path.exists(file_path):
        os.remove(file_path)
        log_message(f'파일 삭제 성공. ({safe_filename})')
    else:
        log_message(f'파일 삭제 실패: 파일이 없음. ({safe_filename})')

    return redirect(url_for('main'))

@app.route('/rename_file', methods=['POST'])
def rename_file():
    old_filename = request.form['old_filename']
    new_filename = request.form['new_filename']
    file_extension = os.path.splitext(old_filename)[1]
    
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message(f'파일 이름 변경 실패: 로그인 상태가 아님. ({old_filename}) -> ({new_filename + file_extension})')
        return redirect(url_for('login')), 403
    
    file_pattern = r'^[a-zA-Z0-9\W_]{1,128}$'
    if not re.match(file_pattern, new_filename):
        log_message(f'파일명 변경 실패: 변경할 파일명 입력 오류. ({old_filename}) -> ({new_filename + file_extension})')
        return redirect(url_for('main')), 400
    
    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
    new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename + file_extension)
    
    if not os.path.exists(old_file_path):
        log_message(f'파일명 변경 실패: 파일이 없음. ({old_filename}) -> ({new_filename + file_extension})')
    
    elif os.path.exists(new_file_path):
        log_message(f'파일명 변경 실패: 변경할 파일명과 같은 이름의 파일이 있음. ({old_filename}) -> ({new_filename + file_extension})')
        
    else:
        os.rename(old_file_path, new_file_path)
        log_message(f'파일명 변경됨: ({old_filename}) -> ({new_filename + file_extension})')
    
    return redirect(url_for('main'))

@app.route('/session_clear', methods=['GET'])
def session_clear():
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        return redirect(url_for('login')), 403

    app.secret_key = secrets.token_hex(32)
    session.clear()
    
    log_message(f'전체 세션 로그아웃 성공.')
    flash('모든 세션이 로그아웃되었습니다. 다시 로그인하세요.', 'success')
    return redirect(url_for('login'))

@app.route('/log/download', methods=['GET'])
def log_download():
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        return redirect(url_for('login')), 403
    
    log_message(f'로그 다운로드 성공.')
    return send_file(os.path.join('log', 'bit-web-server.log'))

@app.route('/log/init', methods=['DELETE'])
def log_init():
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message('로그 초기화 실패: 로그인 상태가 아님.')
        return redirect(url_for('login'))
    
    try:
        admin_id = request.args.get('admin_id')
        admin_pw = request.args.get('admin_pw')
    except KeyError:
        return redirect(url_for('main')), 400
    
    if judg_admin_credentials(admin_id, admin_pw):
        with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
            log_file.write('')
        app.secret_key = secrets.token_hex(32)
        log_message('로그 초기화 성공.')
        return jsonify({'message': 'Logs have been successfully initialized'}), 200

    else:
        log_message('로그 초기화 실패: 관리자 정보가 올바르지 않음.')
        return jsonify({'error': 'Invalid admin credentials'}), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('404_not_found.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500_internal_server_error.html'), 500

# @app.errorhandler(Exception)
# def handle_error(error):
#     log_message(f'cmd: {error}')
#     print(f"Error: {error}")
#     return render_template('exception_handler.html'), 400

def judg_admin_credentials(_input_id: str, _input_pw: str) -> bool:
    load_dotenv(override=True)
    
    admin_id_hash = os.environ.get('ADMIN_ID')
    admin_pw_hash = os.environ.get('ADMIN_PW')
    dev_id_hash = os.environ.get('DEV_ID')
    dev_pw_hash = os.environ.get('DEV_PW')
    
    if check_password_hash(admin_id_hash, _input_id) and check_password_hash(admin_pw_hash, _input_pw):
        return True
    elif check_password_hash(dev_id_hash, _input_id) and check_password_hash(dev_pw_hash, _input_pw):
        return True
    else:
        return False

def initialize_admin():
    if not os.environ.get('ADMIN_ID') or not os.environ.get('ADMIN_PW'):
        init_username_hash = 'scrypt:32768:8:1$XCyXHS2UO1qjsBbu$c94f35f4886641f57b057a5a0d3446ef15a8edda73c97a6464bd552ec9b4f44178928f56bbfd33243ad190da093ee6cca5ebe324a9212cbe5ce7d1185dafe2d3'
        init_password_hash = 'scrypt:32768:8:1$CI8UJcNVUSr6gnmn$d407d1aea3de748812252fad80a575cf67cc07c548e7913acc07b3dfc12434b3614fa576a9f283afee8f92df2c90e96bc01754aa7ea0078d91e2ff9300bab738'
        update_env('ADMIN_ID', init_username_hash)
        update_env('ADMIN_PW', init_password_hash)
        log_message('관리자 계정 초기화됨.', write_for_server=True)

if __name__ == '__main__':
    log_message('서버 시작됨', write_for_server=True)
    initialize_admin()
    app.run(host=SERVER_IP, port=SERVER_PORT, debug=True)
    log_message('서버 종료됨', write_for_server=True)
