from rgbmatrix import RGBMatrix
from modules.matrix_manager.pages import MatrixPages
import modules.utils as utils
import modules.config as config
from PIL import ImageDraw

matrix_pages = MatrixPages()
matrix = RGBMatrix(options = config.MATRIX_OPTIONS)
MATRIX_SIZE = (matrix.width, matrix.height)

IS_EXITED = False

def print_internet_status(display):
    import modules.info_manager as info_manager
    draw = ImageDraw.Draw(display)
    
    if info_manager.service.network.is_internet_connected == False:
        set_loca = [125, 35]
        draw = ImageDraw.Draw(display)
        draw.fontmode="1"
        draw.rectangle([(set_loca[0], set_loca[1]), (set_loca[0]+95, set_loca[1]+25)], outline="white", fill="black")
        draw.bitmap((set_loca[0]+1, set_loca[1]+1),  config.NO_WIFI_ICON, "red")
        draw.text((set_loca[0]+25, set_loca[1]+2), "인터넷 연결을", "white", config.SCD4_FONT_10)
        draw.text((set_loca[0]+25 , set_loca[1]+13), "확인해주세요.", "white", config.SCD4_FONT_10)
    
    return display

def refresh(display, status_prt: bool = True, is_exit_signal: bool = False):
    if IS_EXITED:
        if is_exit_signal == False:
            return
    if status_prt:
        display = print_internet_status(display)
           
    matrix.SetImage(display.convert('RGB'))