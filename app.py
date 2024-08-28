import os
import secrets
from dotenv import load_dotenv
from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_jwt_extended import *
from werkzeug.utils import secure_filename

from auth import login_required, check_login
from src.utils import *
import router.main as router

application = Flask(import_name=__name__)
application.register_blueprint(router.bp)
application.secret_key = secrets.token_hex(32)

load_dotenv()
WEB_HOST = os.environ.get('WEB_HOST', '0.0.0.0')
WEB_PORT = os.environ.get('WEB_PORT', 80)

# main route
@application.route('/')
@login_required
def home():
    return render_template('index.html', client_ip=get_client_ip(request), client_id=session.get('userid'), client_name=session.get('username'))

@application.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        _input_id = request.form.get('userid')
        _input_pw = request.form.get('userpw')
        
        if not _input_id or not _input_pw:
            flash('로그인 실패: 아이디와 비밀번호를 입력해주세요.', 'warning')
            return redirect(url_for('login'))

        # (NAME, LEVEL)
        login_rst = check_login(_input_id, _input_pw)
        if login_rst != False:
            if (login_rst[1] in [0, 1]) == False:
                flash('로그인 실패: 권한이 없습니다.', 'error')
                return redirect(url_for('login'))
            
            session['userid'] = _input_id
            session['username'] = login_rst[0]
            session['userlevel'] = login_rst[1]
            flash(f'({session.get('userid')}) 로그인되었습니다.', 'success')
            return redirect(url_for('home'))
        else:
            flash('로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', client_ip=get_client_ip(request))

@application.route('/logout')
@login_required
def logout():
    flash(f'({session.get('userid')}) 로그아웃되었습니다.', 'warning')
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('userlevel', None)
    return redirect(url_for('login'))

# error handlers
@application.errorhandler(404)
def error_404(e):
    return render_template('error/404.html'), 404

@application.errorhandler(405)
def error_405(e):
    return render_template('error/405.html'), 405

# start application
if __name__ == '__main__':
    application.run(WEB_HOST, WEB_PORT, debug=True)
