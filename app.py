import os
import datetime
from flask import Flask, request, render_template, session, redirect, url_for, flash, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets
import re
from dotenv import load_dotenv, set_key, find_dotenv
import socket

load_dotenv()

HOST_IP = '192.168.1.81'
HOST_PORT = 80
HOST_DEBUG = False

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = set(['mp4', 'wmv', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif'])
LOG_FILE = os.path.join(os.getcwd(), 'log', 'bit-web-server.log')
MAX_STORAGE = 1024 * 1024 * 1024 * 1.5  # 1GB

def now_time() -> str:
    now = datetime.datetime.now()
    f_time = now.strftime("%Y/%m/%d %H:%M:%S.%f")
    return f_time

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_env(key: str, value: str):
    env_path = find_dotenv()
    set_key(env_path, key, value)
    load_dotenv(override=True)  # Reload the .env file to get updated values

def get_client_ip(request) -> str:
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

def format_log_message(content: str) -> str:
    return f"{now_time()} [{get_client_ip(request)}] : {content}"

def log_message(content: str, write_for_server: bool | None = False):
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))
    
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        if write_for_server:
            log_file.write('\n' + f"{now_time()} SERVER : {content}")
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
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"

def get_usage_percentage(used, total):
    use_per = (used / total) * 100
    return f"{use_per:.2f}"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secrets.token_hex(32)

def get_admin_credentials():
    load_dotenv(override=True)  # Ensure the .env file is loaded to get updated values
    username_hash = os.environ.get('ADMIN_ID')
    password_hash = os.environ.get('ADMIN_PW')
    return username_hash, password_hash

# manage page
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
            filename = f"{base}({counter}){ext}"
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
        username = request.form['username']
        password = request.form['password']
        
        username_hash, password_hash = get_admin_credentials()
        if check_password_hash(username_hash, username) and check_password_hash(password_hash, password):
            session['logged_in'] = True
            log_message('로그인 성공.')
            flash('로그인 성공.', 'success')
            
            return redirect(url_for('main'))
        
        else:
            log_message(f'로그인 실패. id({username})pw({password})')
            flash('로그인 실패. 관리자 정보가 올바르지 않음.', 'danger')
        
        return render_template('login.html')

@app.route('/logout')
def logout():
    if session.pop('logged_in', None):
        log_message(f'로그아웃 됨.')
    return redirect(url_for('login'))

@app.route('/admin_settings', methods=['GET', 'POST'])
def admin_settings():
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message('관리자 정보 변경 실패: 로그인 상태가 아님.')
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template('admin_settings.html')
    
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        old_password = request.form['old-password']
        old_username = request.form['old-username']
        
        if not (new_username and new_password):
            log_message('관리자 정보 변경 실패: 입력값 오류.')
            return redirect(url_for('main'))
        
        username_hash, password_hash = get_admin_credentials()
        if not check_password_hash(password_hash, old_password):
            log_message('관리자 정보 변경 실패: 비밀번호 오류.')
            return redirect(url_for('main'))
        
        if not check_password_hash(username_hash, old_username):
            log_message('관리자 정보 변경 실패: 아이디 오류.')
            return redirect(url_for('main'))
        
        id_pattern = r'^[a-zA-Z0-9\W_]{4,64}$'
        if not re.match(id_pattern, new_username):
            log_message('관리자 정보 변경 실패: 변경할 ID 입력 오류.')
            return redirect(url_for('main'))
        
        pw_pattern = r'^[a-zA-Z0-9\W_]{8,256}$'
        if not re.match(pw_pattern, new_password):
            log_message('관리자 정보 변경 실패: 변경할 PW 입력 오류.')
            return redirect(url_for('main'))
        
        new_username_hash = generate_password_hash(new_username)
        new_password_hash = generate_password_hash(new_password)
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
        log_message(f'파일 열람 실패: 로그인 상태가 아님. ({filename})')
        return redirect(url_for('main'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        # log_message(f'파일 열람 성공. ({filename})')
        return send_file(os.path.join('uploads', filename))
    else:
        log_message(f'파일 열람 실패: 파일이 없음. ({filename})')

@app.route('/download/<string:filename>')
def download_file(filename):
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message(f'다운로드 실패: 로그인 상태가 아님. ({filename})')
        return redirect(url_for('main'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        log_message(f'다운로드 성공. ({filename})')
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    else:
        log_message(f'다운로드 실패: 파일이 없음. ({filename})')
        return redirect(url_for('main'))

@app.route('/delete_file', methods=['POST'])
def delete_file():
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message(f'파일 삭제 실패: 로그인 상태가 아님. ({filename})')
        return redirect(url_for('login'))
    
    filename = request.form['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        log_message(f'파일 삭제 성공. ({filename})')
    else:
        log_message(f'파일 삭제 실패: 파일이 없음. ({filename})')
    
    return redirect(url_for('main'))

@app.route('/rename_file', methods=['POST'])
def rename_file():
    old_filename = request.form['old_filename']
    new_filename = request.form['new_filename']
    file_extension = os.path.splitext(old_filename)[1]
    
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message(f'파일 이름 변경 실패: 로그인 상태가 아님. ({old_filename}) -> ({new_filename + file_extension})')
        return redirect(url_for('login'))
    
    file_pattern = r'^[a-zA-Z0-9\W_]{1,128}$'
    if not re.match(file_pattern, new_filename):
        log_message(f'파일명 변경 실패: 변경할 파일명 입력 오류. ({old_filename}) -> ({new_filename + file_extension})')
        return redirect(url_for('main'))
    
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
        log_message(f'모든 세션 로그아웃 실패: 로그인 상태가 아님.')
        return redirect(url_for('login'))

    app.secret_key = secrets.token_hex(32)
    log_message(f'모든 세션 로그아웃 성공.')
    flash('모든 세션이 로그아웃되었습니다. 다시 로그인하세요.', 'success')
    return redirect(url_for('login'))

@app.route('/log/download', methods=['GET'])
def log_download():
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message(f'로그 다운로드 실패: 로그인 상태가 아님.')
        return redirect(url_for('login'))
    log_message(f'로그 다운로드 성공.')
    return send_file(os.path.join('log', 'bit-web-server.log'))
    
@app.route('/log/init', methods=['DELETE'])
def log_init():
    if not session.get('logged_in'):
        flash('로그인 후 작업하세요.')
        log_message('로그 초기화 실패: 로그인 상태가 아님.')
        return redirect(url_for('login'))
    
    admin_id = request.args.get('admin_id')
    admin_pw = request.args.get('admin_pw')
    
    username_hash, password_hash = get_admin_credentials()
    if check_password_hash(username_hash, admin_id) and check_password_hash(password_hash, admin_pw):
        with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
            log_file.write('')
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

@app.errorhandler(Exception)
def handle_error(error):
    log_message(f'에러 발생: {error}')
    print(f"Error: {error}")
    return render_template('exception_handler.html', error=error), 400

def initialize_admin():
    if not os.environ.get('ADMIN_ID') or not os.environ.get('ADMIN_PW'):
        username = 'admin'
        password = '12341234'
        new_username_hash = generate_password_hash(username)
        new_password_hash = generate_password_hash(password)
        update_env('ADMIN_ID', new_username_hash)
        update_env('ADMIN_PW', new_password_hash)
        log_message('관리자 계정 초기화됨: .env 관리자 계정 값 읽기 실패.', write_for_server=True)

if __name__ == '__main__':
    log_message('서버 시작됨', write_for_server=True)
    initialize_admin()
    app.run(host=HOST_IP, port=HOST_PORT, debug=HOST_DEBUG)
    log_message('서버 종료됨', write_for_server=True)
