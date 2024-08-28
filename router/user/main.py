from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from auth import login_required, regi_account, get_account, del_account
import src.utils as utils

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/')
@login_required
def home():
    return render_template('user/index.html', accounts=get_account())

@bp.route('/regi', methods=['GET', 'POST'])
# @login_required
def user_regi():
    if request.method == 'POST':
        _regi_id = request.form.get('regi_userid')
        _regi_pw = request.form.get('regi_userpw')
        _regi_name = request.form.get('regi_username')
        _regi_level = request.form.get('regi_level')
        
        rst = regi_account(_regi_id, _regi_pw, _regi_name, _regi_level)
        
        if rst == True:
            flash('계정이 생성되었습니다.', 'success')
        else:
            flash('계정 생성에 실패했습니다.', 'error')
        return redirect(url_for('router.user.home'))
    
    return render_template('user/regi.html')

@bp.route('/del', methods=['GET', 'POST'])
@login_required
def user_del():
    if request.method == 'POST':
        _del_id = request.form.get('del_userid')
        _del_pw = request.form.get('del_userpw')
        
        rst = del_account(_del_id, _del_pw, session.get('userlevel'))
        
        if rst == True:
            flash('계정이 삭제되었습니다.', 'success')
        else:
            flash('계정 삭제에 실패했습니다.', 'error')
        return redirect(url_for('router.user.home'))
    
    return render_template('user/del.html', accounts=get_account())