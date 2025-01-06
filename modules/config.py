import os
import json
from PIL import Image, ImageFont
from rgbmatrix import RGBMatrixOptions
import modules.utils as utils

PWR_PATH = os.getcwd()
OPTION_PATH = os.path.join(PWR_PATH, 'src', 'option.json')

# Required variables
with open(OPTION_PATH, 'r') as f:
    OPTIONS = json.load(f)
SERVICE_KEY = utils.get_env_key('SERVICE_KEY')

# Matrix optiokn
MATRIX_OPTIONS = RGBMatrixOptions()
MATRIX_OPTIONS.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
MATRIX_OPTIONS.rows = 32
MATRIX_OPTIONS.cols = 64
MATRIX_OPTIONS.chain_length = 7
MATRIX_OPTIONS.pixel_mapper_config = "V-mapper;Rotate:90" # https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/examples-api-use#remapping-coordinates
MATRIX_OPTIONS.pwm_lsb_nanoseconds = 50
MATRIX_OPTIONS.gpio_slowdown = 4
MATRIX_OPTIONS.pwm_bits = 5
MATRIX_OPTIONS.pwm_dither_bits = 0
MATRIX_OPTIONS.show_refresh_rate = False

# Font path
FONT_PATH = os.path.join(os.getcwd(), 'src', 'fonts')
SCD4_FONT_8  = ImageFont.truetype(os.path.join(FONT_PATH, 'SCDream4.otf'), 8)
SCD4_FONT_10 = ImageFont.truetype(os.path.join(FONT_PATH, 'SCDream4.otf'), 11)
SCD4_FONT_12 = ImageFont.truetype(os.path.join(FONT_PATH, 'SCDream4.otf'), 12)
SCD4_FONT_14 = ImageFont.truetype(os.path.join(FONT_PATH, 'SCDream4.otf'), 14)
SCD4_FONT_16 = ImageFont.truetype(os.path.join(FONT_PATH, 'SCDream5.otf'), 16)
SCD4_FONT_26 = ImageFont.truetype(os.path.join(FONT_PATH, 'SCDream8.otf'), 26)

# Icon load
ICON_PATH = os.path.join(os.getcwd(), 'src', 'icon')
BUS_ICON_PATH = os.path.join(ICON_PATH, 'bus.png')
BUS_ICON = Image.open(BUS_ICON_PATH)
BUS_LP_ICON_PATH = os.path.join(ICON_PATH, 'bus_lp.png')
BUS_LP_ICON = Image.open(BUS_LP_ICON_PATH)
NO_WIFI_ICON_PATH = os.path.join(ICON_PATH, 'no_wifi.png')
NO_WIFI_ICON = Image.open(NO_WIFI_ICON_PATH)