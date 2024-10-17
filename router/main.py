from flask import Blueprint
import router.manage.main as manage
import router.file.main as file
import router.user.main as user

bp = Blueprint('router', __name__)

bp.register_blueprint(manage.bp)
bp.register_blueprint(file.bp)
bp.register_blueprint(user.bp)