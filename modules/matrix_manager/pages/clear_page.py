import modules.matrix_manager as matrix_manager
from PIL import Image, ImageDraw, ImageFont

def show_clear_page():
    canvas = Image.new('RGBA', matrix_manager.MATRIX_SIZE, (0, 0, 0, 0))
    matrix_manager.refresh(canvas.convert("RGB"))
    return 0