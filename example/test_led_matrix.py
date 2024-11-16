import os
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
from PIL import Image, ImageDraw, ImageFont

options = RGBMatrixOptions()
options.hardware_mapping = 'adafruit-hat'
options.rows = 32
options.cols = 64
options.chain_length = 7
# https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/examples-api-use#remapping-coordinates
options.pixel_mapper_config = "V-mapper;Rotate:90"
options.pwm_lsb_nanoseconds = 50
options.gpio_slowdown = 4
options.pwm_bits = 5
options.pwm_dither_bits = 0
options.show_refresh_rate = True

matrix = RGBMatrix(options=options)
matrix_size = (matrix.width, matrix.height)

def refresh(display):
    matrix.SetImage(display.convert('RGB'))

def display_image():
    image_path = './src/icon'
    station_icon = Image.open(os.path.join(image_path, 'everline_station.png'))
    train_icon = Image.open(os.path.join(image_path, 'everline_train.png'))

    RECTANGLE_TOP = 51
    RECTANGLE_BOTTOM = 55
    ICON_MARGIN = 20

    # Calculate positions to center the icon within the rectangle and at 20 pixels from left and right
    center_x = (matrix_size[0] - station_icon.width) // 2
    center_y = (RECTANGLE_TOP+1) + (RECTANGLE_BOTTOM - RECTANGLE_TOP - station_icon.height) // 2
    left_x = ICON_MARGIN
    right_x = matrix_size[0] - station_icon.width - ICON_MARGIN

    # Draw Image
    canvas = Image.new('RGB', matrix_size, "black")
    draw = ImageDraw.Draw(canvas)
    draw.fontmode = "1"
    
    station_title = "고진역"
    station_title_center = (matrix_size[0] - len(station_title) * 6) // 2
    
    train_x = -20
    while True:
        draw.rectangle([(0, 0), matrix_size], fill=(0, 0, 0))
        draw.text((station_title_center, 0), station_title, fill=(255, 255, 255))
        draw.rectangle([(0, RECTANGLE_TOP), (matrix_size[0], RECTANGLE_BOTTOM)], fill=(100, 100, 100))
        canvas.paste(station_icon, (center_x, center_y))
        canvas.paste(station_icon, (left_x, center_y))
        canvas.paste(station_icon, (right_x, center_y))
        
        canvas.paste(train_icon, (train_x, center_y))
        
        refresh(canvas)
        time.sleep(0.01)
        train_x += 1
        if train_x > matrix_size[0]:
            train_x = -20

try:
    display_image()
except KeyboardInterrupt:
    pass