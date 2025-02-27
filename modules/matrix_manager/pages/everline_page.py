import datetime
import os
import time
from PIL import Image, ImageDraw, ImageFont
import modules.config as config
import modules.info_manager as info_manager
import modules.matrix_manager as matrix_manager

def show_everline_page(_show_time_sec: int = 15):
    ev_options = config.OPTIONS['everline']
    station_icon = config.EVERLINE_STATION_ICON
    train_icon = config.EVERLINE_TRAIN_ICON
    reverse_train_icon = train_icon.transpose(Image.FLIP_LEFT_RIGHT)

    RECTANGLE_TOP = 30

    # Calculate positions to center the icon within the rectangle and at 20 pixels from left and right
    center_x = (matrix_manager.MATRIX_SIZE[0] - station_icon.width) // 2
    center_y = RECTANGLE_TOP + (RECTANGLE_TOP+4 - RECTANGLE_TOP - station_icon.height) // 2
    left_x = 5
    right_x = 206
    train_center_x = 102
    train_back_x = 2
    train_next_x = 202

    # Draw Image
    canvas = Image.new('RGBA', matrix_manager.MATRIX_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.fontmode = "1"
    
    back_station = ev_options['backStation']
    base_station = ev_options['baseStation']
    next_station = ev_options['nextStation']
    
    station_title = f"[에버라인 운행정보] {info_manager.service.everline.STATION_CODE[base_station]}역"
    title_bbox = config.SCD4_FONT_11.getbbox(station_title)
    title_width = title_bbox[2] - title_bbox[0]
    station_title_center = (matrix_manager.MATRIX_SIZE[0] - title_width) // 2
    
    train_x = -20
    start_time = time.time()
    while True:
        if time.time() - start_time > _show_time_sec:
            break
        
        now_hhmm = datetime.datetime.now().strftime('%H%M')
        title_now_hhmm = datetime.datetime.now().strftime('%H:%M')
        train_infos = info_manager.service.everline_api.get_train_info()
        # 인터넷 연결 시에만 열차 정보 로드
        if info_manager.service.network.is_internet_connected == False:
            train_infos = False
        
        draw.rectangle([(0, 0), matrix_manager.MATRIX_SIZE], fill=(0, 0, 0, 0))
        draw.text((station_title_center, 0), station_title, fill=(255, 255, 255), font=config.SCD4_FONT_11)
        draw.text((195, 0), f"{title_now_hhmm}", fill=(150, 150, 150), font=ImageFont.load_default(size=10))
        draw.line([(0, RECTANGLE_TOP+1), (matrix_manager.MATRIX_SIZE[0], RECTANGLE_TOP+1)], fill=(100, 100, 100, 255), width=5)
        
        # Draw train
        if train_infos != None:
            for train_info in train_infos:
                if train_info['StCode'] in [base_station, back_station, next_station]:
                    if train_info['StatusCode'] == info_manager.service.everline.TRAIN_START:
                        if train_info['updownCode'] == info_manager.service.everline.TRAIN_UPWARD:
                            if train_info['StCode'] == base_station:
                                canvas.paste(train_icon, (train_center_x-int(train_info['driveRate']), center_y-4), train_icon)
                            elif train_info['StCode'] == back_station:
                                canvas.paste(train_icon, (train_back_x-int(train_info['driveRate']), center_y-4), train_icon)
                            elif train_info['StCode'] == next_station:
                                canvas.paste(train_icon, (train_next_x-int(train_info['driveRate']), center_y-4), train_icon)
                                
                        elif train_info['updownCode'] == info_manager.service.everline.TRAIN_DOWNWARD:
                            if train_info['StCode'] == base_station:
                                canvas.paste(reverse_train_icon, (train_center_x+int(train_info['driveRate']), center_y-4), reverse_train_icon)
                            elif train_info['StCode'] == back_station:
                                canvas.paste(reverse_train_icon, (train_back_x+int(train_info['driveRate']), center_y-4), reverse_train_icon)
                            elif train_info['StCode'] == next_station:
                                canvas.paste(reverse_train_icon, (train_next_x+int(train_info['driveRate']), center_y-4), reverse_train_icon)
                    
                    if train_info['StatusCode'] == info_manager.service.everline.TRAIN_STOP:
                        if train_info['updownCode'] == info_manager.service.everline.TRAIN_UPWARD:
                            if train_info['StCode'] == base_station:
                                canvas.paste(train_icon, (train_center_x, center_y-4), train_icon)
                            elif train_info['StCode'] == back_station:
                                canvas.paste(train_icon, (train_back_x, center_y-4), train_icon)
                            elif train_info['StCode'] == next_station:
                                canvas.paste(train_icon, (train_next_x, center_y-4), train_icon)
                        
                        elif train_info['updownCode'] == info_manager.service.everline.TRAIN_DOWNWARD:
                            if train_info['StCode'] == base_station:
                                canvas.paste(reverse_train_icon, (train_center_x, center_y-4), reverse_train_icon)
                            elif train_info['StCode'] == back_station:
                                canvas.paste(reverse_train_icon, (train_back_x, center_y-4), reverse_train_icon)
                            elif train_info['StCode'] == next_station:
                                canvas.paste(reverse_train_icon, (train_next_x, center_y-4), reverse_train_icon)
        
        # Draw station icons
        canvas.paste(station_icon, (center_x, center_y), station_icon)
        draw.text((left_x, RECTANGLE_TOP+8), f"{info_manager.service.everline.STATION_CODE[back_station]}역", fill=(200, 200, 255, 255), font=config.SCD4_FONT_8)
        canvas.paste(station_icon, (left_x, center_y), station_icon)
        draw.text((center_x-5, RECTANGLE_TOP+8), f"{info_manager.service.everline.STATION_CODE[base_station]}역", fill=(200, 200, 255, 255), font=config.SCD4_FONT_8)
        canvas.paste(station_icon, (right_x, center_y), station_icon)
        draw.text((right_x-11, RECTANGLE_TOP+8), f"{info_manager.service.everline.STATION_CODE[next_station]}역", fill=(200, 200, 255, 255), font=config.SCD4_FONT_8)
        
        # Draw train interval
        train_interval = None
        if datetime.date.today().weekday()  >= 5:
            train_interval = info_manager.service.everline.get_train_interval(now_hhmm, True)
        else:
            train_interval = info_manager.service.everline.get_train_interval(now_hhmm)
        
        if train_interval != None:
            train_interval_str = f"열차는 매 {train_interval}분마다 운행합니다."
        else:
            train_interval_str = "열차가 운행하지 않는 시각입니다."
        draw.text((0, matrix_manager.MATRIX_SIZE[1]-11), train_interval_str, fill=(255, 255, 255, 255), font=config.SCD4_FONT_10)
        
        matrix_manager.refresh(canvas.convert("RGB"))
        time.sleep(0.01)
        train_x += 1
        if train_x > matrix_manager.MATRIX_SIZE[0]:
            train_x = -20
