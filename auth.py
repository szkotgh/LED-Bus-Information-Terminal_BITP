from functools import wraps
from flask import session, redirect, url_for, flash
import sqlite3
import base64
import src.utils as utils

user_db = sqlite3.connect('user.db', check_same_thread=False)
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
    LEVEL INTEGER DEFAULT 9
)
''')
user_db.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('로그인 후 이용하세요.', 'warning')
            return redirect(url_for('login'))
        
        session['lastworktime'] = utils.get_current_time() # Save current time in session
        
        return f(*args, **kwargs)
    return decorated_function

def check_login(_input_id, _input_pw):
    if [None, ''] in [[_input_id, _input_pw]]:
        return False
    
    for row in user_cursor.execute('SELECT * FROM USERS'):
        if row[0] == _input_id and row[1] == utils.gen_hash(_input_pw):
            return row[2], row[3] # (NAME, LEVEL)

    return False

def regi_account(_regi_id, _regi_pw, _regi_name, _regi_level):
    if [None, ''] in [[_regi_id, _regi_pw, _regi_name]]:
        return False
    
    _regi_pw_hash = utils.gen_hash(_regi_pw)
    
    if _regi_level == None or (_regi_level not in ["0", "1", "9"]):
        _regi_level = 9
    
    user_cursor.execute('SELECT * FROM USERS WHERE ID=?', (_regi_id,))
    if user_cursor.fetchone():
        return False
    
    user_cursor.execute('INSERT OR IGNORE INTO USERS (ID, PW, NAME, LEVEL) VALUES (?, ?, ?, ?)', (_regi_id, _regi_pw_hash, _regi_name, _regi_level))
    user_db.commit()
    
    return True

def del_account(_del_id, _del_pw, user_level):
    if [None, ''] in [[_del_id, _del_pw]]:
        return False
    
    rst = check_login(_del_id, _del_pw)
    if rst != False:
        if rst[1] < user_level:
            flash("권한이 없습니다.", 'error')
            return False
        
        user_cursor.execute('DELETE FROM USERS WHERE ID=?', (_del_id, ))
        user_db.commit()
        return True
    else:
        flash("아이디/비밀번호 오류입니다.", 'error')
        return False

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