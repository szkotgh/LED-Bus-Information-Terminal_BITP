import os
import sys
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
sys.path.append(os.path.join(os.getcwd()))
from module.everline_api import everline_api

everline = everline_api.EverlineAPI()
everline.auto_update(2)

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
options.show_refresh_rate = False

matrix = RGBMatrix(options=options)
matrix_size = (matrix.width, matrix.height)

def refresh(display):
    matrix.SetImage(display.convert('RGB'))

def display_image():
    image_path = './src/icon'
    station_icon = Image.open(os.path.join(image_path, 'everline_station.png')).convert("RGBA")
    train_icon = Image.open(os.path.join(image_path, 'everline_train.png')).convert("RGBA")
    reverse_train_icon = train_icon.transpose(Image.FLIP_LEFT_RIGHT)
    font_path = os.path.join(os.getcwd(), 'src', 'fonts')
    font8  = ImageFont.truetype(os.path.join(font_path, 'SCDream5.otf'), 8)
    font10 = ImageFont.truetype(os.path.join(font_path, 'SCDream5.otf'), 10)
    font11 = ImageFont.truetype(os.path.join(font_path, 'SCDream4.otf'), 11)
    font12 = ImageFont.truetype(os.path.join(font_path, 'SCDream4.otf'), 12)
    font14 = ImageFont.truetype(os.path.join(font_path, 'SCDream4.otf'), 14)
    font16 = ImageFont.truetype(os.path.join(font_path, 'SCDream5.otf'), 16)
    font26 = ImageFont.truetype(os.path.join(font_path, 'SCDream8.otf'), 26)

    RECTANGLE_TOP = 30

    # Calculate positions to center the icon within the rectangle and at 20 pixels from left and right
    center_x = (matrix_size[0] - station_icon.width) // 2
    center_y = RECTANGLE_TOP + (RECTANGLE_TOP+4 - RECTANGLE_TOP - station_icon.height) // 2
    left_x = 5
    right_x = 206
    train_center_x = 102
    train_back_x = 2
    train_next_x = 202

    # Draw Image
    canvas = Image.new('RGBA', matrix_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.fontmode = "1"
    
    back_station = "Y110"
    base_station = "Y111"
    next_station = "Y112"
    
    station_title = f"[에버라인 운행정보] {everline_api.STATION_CODE[base_station]}역"
    title_bbox = font11.getbbox(station_title)
    title_width = title_bbox[2] - title_bbox[0]
    station_title_center = (matrix_size[0] - title_width) // 2
    
    train_x = -20
    while True:
        everline.auto_update(2)
        
        now_hhmm = datetime.datetime.now().strftime('%H%M')
        title_now_hhmm = datetime.datetime.now().strftime('%H:%M')
        train_infos = everline.get_train_info()
        
        draw.rectangle([(0, 0), matrix_size], fill=(0, 0, 0, 0))
        draw.text((station_title_center, 0), station_title, fill=(255, 255, 255), font=font11)
        draw.text((195, 0), f"{title_now_hhmm}", fill=(150, 150, 150), font=ImageFont.load_default(size=10))
        draw.line([(0, RECTANGLE_TOP+1), (matrix_size[0], RECTANGLE_TOP+1)], fill=(100, 100, 100, 255), width=5)
        
        # Draw train
        if train_infos != None:
            for train_info in train_infos:
                if train_info['StCode'] in [base_station, back_station, next_station]:
                    if train_info['StatusCode'] == everline_api.TRAIN_START:
                        if train_info['updownCode'] == everline_api.TRAIN_UPWARD:
                            if train_info['StCode'] == base_station:
                                canvas.paste(train_icon, (train_center_x-int(train_info['driveRate']), center_y-4), train_icon)
                            elif train_info['StCode'] == back_station:
                                canvas.paste(train_icon, (train_back_x-int(train_info['driveRate']), center_y-4), train_icon)
                            elif train_info['StCode'] == next_station:
                                canvas.paste(train_icon, (train_next_x-int(train_info['driveRate']), center_y-4), train_icon)
                                
                        elif train_info['updownCode'] == everline_api.TRAIN_DOWNWARD:
                            if train_info['StCode'] == base_station:
                                canvas.paste(reverse_train_icon, (train_center_x+int(train_info['driveRate']), center_y-4), reverse_train_icon)
                            elif train_info['StCode'] == back_station:
                                canvas.paste(reverse_train_icon, (train_back_x+int(train_info['driveRate']), center_y-4), reverse_train_icon)
                            elif train_info['StCode'] == next_station:
                                canvas.paste(reverse_train_icon, (train_next_x+int(train_info['driveRate']), center_y-4), reverse_train_icon)
                    
                    if train_info['StatusCode'] == everline_api.TRAIN_STOP:
                        if train_info['updownCode'] == everline_api.TRAIN_UPWARD:
                            if train_info['StCode'] == base_station:
                                canvas.paste(train_icon, (train_center_x, center_y-4), train_icon)
                            elif train_info['StCode'] == back_station:
                                canvas.paste(train_icon, (train_back_x, center_y-4), train_icon)
                            elif train_info['StCode'] == next_station:
                                canvas.paste(train_icon, (train_next_x, center_y-4), train_icon)
                        
                        elif train_info['updownCode'] == everline_api.TRAIN_DOWNWARD:
                            if train_info['StCode'] == base_station:
                                canvas.paste(reverse_train_icon, (train_center_x, center_y-4), reverse_train_icon)
                            elif train_info['StCode'] == back_station:
                                canvas.paste(reverse_train_icon, (train_back_x, center_y-4), reverse_train_icon)
                            elif train_info['StCode'] == next_station:
                                canvas.paste(reverse_train_icon, (train_next_x, center_y-4), reverse_train_icon)
        
        # Draw station icons
        canvas.paste(station_icon, (center_x, center_y), station_icon)
        draw.text((left_x, RECTANGLE_TOP+8), f"{everline_api.STATION_CODE[back_station]}역", fill=(200, 200, 255, 255), font=font8)
        canvas.paste(station_icon, (left_x, center_y), station_icon)
        draw.text((center_x-5, RECTANGLE_TOP+8), f"{everline_api.STATION_CODE[base_station]}역", fill=(200, 200, 255, 255), font=font8)
        canvas.paste(station_icon, (right_x, center_y), station_icon)
        draw.text((right_x-11, RECTANGLE_TOP+8), f"{everline_api.STATION_CODE[next_station]}역", fill=(200, 200, 255, 255), font=font8)
        
        # Draw train interval
        train_interval = None
        if datetime.date.today().weekday()  >= 5:
            train_interval = everline_api.get_train_interval(now_hhmm, True)
        else:
            train_interval = everline_api.get_train_interval(now_hhmm)
        
        if train_interval != None:
            draw.text((0, matrix_size[1]-11), f"열차는 매 {train_interval}분마다 운행합니다.", fill=(255, 255, 255, 255), font=font10)
        else:
            draw.text((0, matrix_size[1]-11), "열차가 운행하지 않는 시각입니다.", fill=(255, 255, 255, 255), font=font10)
            
        refresh(canvas.convert("RGB"))
        time.sleep(0.01)
        train_x += 1
        if train_x > matrix_size[0]:
            train_x = -20

try:
    display_image()
except KeyboardInterrupt:
    pass