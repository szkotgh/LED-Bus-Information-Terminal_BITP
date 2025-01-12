import time
from PIL import Image, ImageDraw, ImageFont
import modules.matrix_manager as matrix_manager
import modules.config as config
import modules.utils as utils

def show_duk_50th_anniversary_page():
    for i in range(1, -460, -1):
        text = [
            "덕영고 50주년!!",
            "50년의 빛나는 역사, 미래를 향한 무궁한 발전을 기원합니다."
        ]
        
        canvas = Image.new('RGB', matrix_manager.MATRIX_SIZE, "black")
        draw = ImageDraw.Draw(canvas)
        draw.fontmode="1"
        
        draw.text((1, 1), text[0], "white", config.SCD4_FONT_26)
        draw.text((i, 32), text[1], "white", config.SCD4_FONT_26)
        
        matrix_manager.refresh(canvas)
        
        if i == 1:
            time.sleep(1)
        time.sleep(0.005)
    time.sleep(1.5)