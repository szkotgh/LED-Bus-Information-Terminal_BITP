from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from auth import login_required, regi_account, get_account, del_account
import src.utils as utils

bp = Blueprint('bit', __name__, url_prefix='/bit')

@bp.route('/', methods=['GET'])
@login_required
def home():
    return render_template('bit/index.html', client_ip=utils.get_client_ip(request), client_id=session.get('userid'),
                           client_name=session.get('username')), 200
