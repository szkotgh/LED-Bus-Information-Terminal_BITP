import module.config as config
from PIL import Image, ImageDraw, ImageFont

matrix = config.matrix

def refresh(self, display, status_prt: bool = True):    
    # display.save('./display.png')k
    matrix.SetImage(display.convert('RGB'))