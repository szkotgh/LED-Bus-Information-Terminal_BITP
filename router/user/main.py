from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from auth import login_required, regi_account, get_account, del_account
import src.utils as utils

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/', methods=['GET'])
@login_required
def home():
    return render_template('user/index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                           client_name=session.get('username'), accounts=get_account()), 200

@bp.route('/regi', methods=['GET', 'POST'])
@login_required
def user_regi():
    if session.get('userlevel', -1) != 0:
        flash("권한이 없습니다.", 'error')
        return redirect(url_for('router.user.home'))
    
    if request.method == 'POST':
        _regi_id = request.form.get('regi_userid')
        _regi_pw = request.form.get('regi_userpw')
        _regi_name = request.form.get('regi_username')
        _regi_level = request.form.get('regi_level')
        
        if (not _regi_id) or (not _regi_pw) or (not _regi_name) or (not _regi_level):
            flash('필요한 정보를 모두 입력해주세요.', 'error')
            return redirect(url_for('router.user.home'))
        
        if 0 != session.get('userlevel'):
            flash('권한이 없습니다.', 'error')
            return redirect(url_for('router.user.home'))
        
        rst = regi_account(_regi_id, _regi_pw, _regi_name, _regi_level)
        
        if rst == True:
            flash('계정이 생성되었습니다.', 'success')
        else:
            flash('계정 생성에 실패했습니다.', 'error')
        return redirect(url_for('router.user.home'))
    
    return render_template('user/regi.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                           client_name=session.get('username')), 200

@bp.route('/delete', methods=['GET', 'POST'])
@login_required
def user_del():
    if session.get('userlevel', -1) != 0:
        flash("권한이 없습니다.", 'error')
        return redirect(url_for('router.user.home')), 200
    
    if request.method == 'POST':
        _del_id = request.form.get('del_userid')
        
        if (not _del_id):
            flash('필요한 정보를 모두 입력해주세요.', 'error')
            return redirect(url_for('router.user.home')), 200
        
        if 0 != session.get('userlevel'):
            flash('권한이 없습니다.', 'error')
            return redirect(url_for('router.user.home')), 200
        
        if _del_id == session.get('userid'):
            flash('자신의 계정은 삭제할 수 없습니다.', 'error')
            return redirect(url_for('router.user.home')), 200
        
        rst = del_account(_del_id)
        
        if rst == True:
            flash('계정이 삭제되었습니다.', 'success')
        else:
            flash('계정 삭제에 실패했습니다.', 'error')
        return redirect(url_for('router.user.home')), 200
    
    return render_template('user/delete.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'), client_name=session.get('username'), accounts=get_account()), 200