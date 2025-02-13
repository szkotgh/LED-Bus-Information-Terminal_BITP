from flask import Blueprint, render_template
import os

control_bp = Blueprint('control', __name__, url_prefix='/control')

@control_bp.route('/')
def index():
    return render_template('control/index.html')

@control_bp.route('/restart_bit')
def restart_bit():
    return 'OK'

@control_bp.route('/reboot')
def reboot():
    return 'OK'