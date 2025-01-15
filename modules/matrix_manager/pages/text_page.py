import time
from PIL import Image, ImageDraw
import modules.config as config
import modules.utils as utils
import modules.matrix_manager as matrix_manager

def show_text_page(_set_text: str | list = "", _first_show_time: int | float = 1, _end_show_time: int | float = 1, _repeat: int = 1, _text_color: str = 'white', _status_prt: bool = True):
    if isinstance(_set_text, str):
        texts = [_set_text]
    elif isinstance(_set_text, list):
        texts = _set_text

    text_widths = [utils.get_text_volume(text, config.SCD4_FONT_12) for text in texts]
    display_width = matrix_manager.MATRIX_SIZE[0]

    canvas = Image.new('RGB', matrix_manager.MATRIX_SIZE, "black")
    draw = ImageDraw.Draw(canvas)
    draw.fontmode = "1"

    for repeat in range(_repeat):
        for i, text in enumerate(texts):
            x_loca_row = [0, 13, 26, 39, 51]
            if i < len(x_loca_row):
                draw.text((1, x_loca_row[i]), str(text), _text_color, config.SCD4_FONT_12)

        matrix_manager.refresh(canvas, status_prt=_status_prt)
        time.sleep(_first_show_time)

        moving_texts = [text for text, width in zip(texts, text_widths) if width > display_width]
        initial_positions = {text: matrix_manager.MATRIX_SIZE[0] for text in moving_texts}

        if not moving_texts:
            time.sleep(_end_show_time)
            if isinstance(_set_text, list) and ( len(_set_text) > 5 ):
                show_text_page(_set_text[5:], _first_show_time, _end_show_time)
            return 0

        while True:
            canvas = Image.new('RGB', matrix_manager.MATRIX_SIZE, "black")
            draw = ImageDraw.Draw(canvas)
            draw.fontmode = "1"

            all_texts_moved = True
            for i, text in enumerate(texts):
                if text in moving_texts:
                    position_x = initial_positions[text]
                    if position_x + utils.get_text_volume(text, config.SCD4_FONT_12) > 0:
                        draw.text((position_x, i * 13), str(text), _text_color, config.SCD4_FONT_12)
                        all_texts_moved = False
                else:
                    x_loca_row = [0, 13, 26, 39, 51]
                    if i < len(x_loca_row):
                        draw.text((1, x_loca_row[i]), str(text), _text_color, config.SCD4_FONT_12)

            matrix_manager.refresh(canvas, status_prt=_status_prt)

            time.sleep(0.01)

            for text in moving_texts:
                initial_positions[text] -= 1

            if all_texts_moved:
                time.sleep(_end_show_time)
                break
    
    if isinstance(_set_text, list) and ( len(_set_text) > 5 ):
        show_text_page(_set_text[5:], _first_show_time, _end_show_time, _repeat)
    
    return 0