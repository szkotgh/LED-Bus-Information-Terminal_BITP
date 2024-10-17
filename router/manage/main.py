from flask import Blueprint, flash, redirect, render_template, request, session, url_for, jsonify

from auth import login_required
import src.utils as utils

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/', methods=['GET'])
@login_required
def home():
    return render_template('manage/index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                           client_name=session.get('username')), 200

@bp.route('/reboot', methods=['GET'])
@login_required
def reboot():
    return 'success'

@bp.route('/system_usage', methods=['GET'])
def get_system_info():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '로그인 후 이용하세요.'}), 401
    return utils.get_system_info()