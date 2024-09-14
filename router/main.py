from flask import Blueprint
import router.bit.main as bit
import router.file.main as file
import router.user.main as user

bp = Blueprint('router', __name__)

bp.register_blueprint(bit.bp)
bp.register_blueprint(file.bp)
bp.register_blueprint(user.bp)