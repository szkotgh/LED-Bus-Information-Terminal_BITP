from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import timedelta
import sqlite3
import base64
import src.utils as utils

user_db = sqlite3.connect('./db/user.db', check_same_thread=False)
user_cursor = user_db.cursor()

# level 정보
# 1: 관리자
# 2: 일반 사용자
# 9: 권한 없음

user_cursor.execute('''
CREATE TABLE IF NOT EXISTS USERS (
    ID TEXT PRIMARY KEY,
    PW TEXT,
    NAME TEXT,
    LEVEL INTEGER DEFAULT 1
)
''')
user_db.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('로그인 후 이용하세요.', 'warning')
            return redirect(url_for('login'))
        
        is_id_exist = False
        for row in user_cursor.execute('SELECT * FROM USERS'):
            if row[0] == session.get('userid'):
                is_id_exist = True
                break
        if is_id_exist == False:
            session.clear()
            flash('존재하지 않는 계정입니다. 다시 로그인하세요.', 'error')
            return redirect(url_for('login'))
        
        if 'lastworktime' in session:
            if utils.convert_now_ftime(session['lastworktime']) < utils.convert_now_ftime(utils.get_now_ftime()) - timedelta(minutes=5):
                session.clear()
                flash('세션이 만료되었습니다. 다시 로그인하세요.', 'error')
                return redirect(url_for('login'))
        
        session['lastworktime'] = utils.get_now_ftime()
        
        return f(*args, **kwargs)
    return decorated_function

def check_login(_input_id, _input_pw):
    if [None, ''] in [[_input_id, _input_pw]]:
        return False
    
    _input_id = str(_input_id)
    _input_pw = str(_input_pw)
    
    for row in user_cursor.execute('SELECT * FROM USERS'):
        if row[0] == _input_id and row[1] == utils.gen_hash(_input_pw):
            #      (NAME, LEVEL)
            return row[2], row[3]

    return False

def regi_account(_regi_id, _regi_pw, _regi_name, _regi_level):
    _regi_pw_hash = utils.gen_hash(_regi_pw)
    
    user_cursor.execute('SELECT * FROM USERS WHERE ID=?', (_regi_id,))
    if user_cursor.fetchone():
        flash("이미 존재하는 아이디입니다.", 'error')
        return False
    
    user_cursor.execute('INSERT OR IGNORE INTO USERS (ID, PW, NAME, LEVEL) VALUES (?, ?, ?, ?)', (_regi_id, _regi_pw_hash, _regi_name, _regi_level))
    user_db.commit()
    
    return True

def del_account(_del_id):
    user_cursor.execute('DELETE FROM USERS WHERE ID=?', (_del_id, ))
    user_db.commit()
    if user_cursor.rowcount == 0:
        flash("존재하지 않는 아이디입니다.", 'error')
        return False
    return True

def get_account():
    accounts = []
    level_grade = {
        0: '관리자',
        1: '일반 사용자',
        9: '권한 없음'
    }
    for row in user_cursor.execute('SELECT * FROM USERS'):
        accounts.append({'id': row[0], 'name': row[2], 'level': level_grade.get(row[3])})
    return accounts