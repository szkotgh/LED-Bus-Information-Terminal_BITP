import time
from PIL import Image, ImageDraw
import modules.config as config
import modules.matrix_manager as matrix_manager

def show_test_page(_test_type: int = 0, _delay_time:int = 1):
    test_color = ["red", "lime", "blue", "white"]
    display = Image.new('RGB', matrix_manager.MATRIX_SIZE, color = 'black')
    draw = ImageDraw.Draw(display)
    
    if _test_type == 0:
        for color in test_color:
            draw.rectangle(((0, 0), (matrix_manager.MATRIX_SIZE[0], matrix_manager.MATRIX_SIZE[1])), color)
            matrix_manager.refresh(display, status_prt=False)
            time.sleep(_delay_time)
    
    elif _test_type == 1:
        for i in range(0, matrix_manager.MATRIX_SIZE[0]):
            for j in range(0, matrix_manager.MATRIX_SIZE[1]):
                draw.point((i, j), test_color[(i+j) % 4])
            matrix_manager.refresh(display, status_prt=False)
            time.sleep(0.01)
        time.sleep(_delay_time)
    
    elif _test_type == 2:
        for y in range(0, matrix_manager.MATRIX_SIZE[1], 7):
            draw.line((0, y, matrix_manager.MATRIX_SIZE[0], y), fill='white')
        for x in range(0, matrix_manager.MATRIX_SIZE[0], 9):
            draw.line((x, 0, x, matrix_manager.MATRIX_SIZE[1]), fill='white')
        matrix_manager.refresh(display, status_prt=False)
        time.sleep(_delay_time)