from flask import Blueprint, render_template
import modules.web_manager.router.control as control_router

router_bp = Blueprint('main', __name__, url_prefix='/')
router_bp.register_blueprint(control_router.control_bp)

@router_bp.route('/')
def index():
    return render_template('index.html')

