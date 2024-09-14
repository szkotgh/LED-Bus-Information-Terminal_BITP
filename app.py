import os
import secrets
from dotenv import load_dotenv
from flask import Flask, flash, render_template, redirect, url_for, request, session
from auth import login_required, check_login
import  src.utils as utils
import router.main as router

application = Flask(import_name=__name__)
application.secret_key = secrets.token_hex(32)
application.config['MAX_CONTENT_LENGTH'] = utils.MAX_UPLOAD_SIZE
application.register_blueprint(router.bp)

load_dotenv()
WEB_HOST = os.environ.get('WEB_HOST', '0.0.0.0')
WEB_PORT = os.environ.get('WEB_PORT', 80)

# main route
@application.route('/')
@login_required
def home():
    return render_template('index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                           client_name=session.get('username')), 200

@application.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        flash('이미 로그인되어 있습니다.', 'warning')
        return redirect(url_for('home'), 302)
    
    if request.method == 'POST':
        _input_id = request.form.get('userid')
        _input_pw = request.form.get('userpw')
        
        if not _input_id or not _input_pw:
            flash('로그인 실패: 아이디와 비밀번호를 입력해주세요.', 'error')
            return redirect(url_for('login'), 400)

        # (NAME, LEVEL)
        login_rst = check_login(_input_id, _input_pw)
        if login_rst != False:
            if (login_rst[1] in [0, 1]) == False:
                flash('로그인 실패: 권한이 없습니다.', 'error')
                return redirect(url_for('login'), 401)
            
            session['userid'] = _input_id
            session['username'] = login_rst[0]
            session['userlevel'] = login_rst[1]
            
            flash(f'({session.get('userid')}) 로그인되었습니다.', 'success')
            return redirect(url_for('home'), 302)
        else:
            flash('로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('login'), 401)

    return render_template('login.html', client_ip=utils.get_client_ip(request))

@application.route('/logout', methods=['GET'])
@login_required
def logout():
    flash(f'({session.get('userid')}) 로그아웃되었습니다.', 'warning')
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('userlevel', None)
    return redirect(url_for('login'), 302)

@application.route('/딸배', methods=['GET'])
def ddalbae():
    user_id = session.get('userid')
    
    if user_id in utils.SPECIAL_USERID:
        return render_template('index_secret.html'), 200
    
    return render_template('error/404.html', client_ip=utils.get_client_ip(request)), 404

# error handlers
@application.errorhandler(404)
def error_404(e):
    return render_template('error/404.html', client_ip=utils.get_client_ip(request)), 404

@application.errorhandler(405)
def error_405(e):
    return render_template('error/405.html', client_ip=utils.get_client_ip(request)), 405

# start application
if __name__ == '__main__':
    application.run(WEB_HOST, WEB_PORT, debug=True)
