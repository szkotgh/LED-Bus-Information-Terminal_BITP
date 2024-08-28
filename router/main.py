from flask import Blueprint
import router.user.main as user

bp = Blueprint('router', __name__)
bp.register_blueprint(user.bp)
