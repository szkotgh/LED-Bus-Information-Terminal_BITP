import datetime
import time
from PIL import Image, ImageDraw
import modules.config as config
import modules.utils as utils
import modules.matrix_manager as matrix_manager
from modules.info_manager.apis.bus_station import BusStationAPI

def show_station_etc_page(_show_station_struct: BusStationAPI, _show_time_sec: int):
    _start_time = datetime.datetime.now()
    
    weather_info = _show_station_struct.station_weather_data
    finedust_info = _show_station_struct.station_finedust_data
    
    x_loca_col       = [0, 70, 77]
    y_loca_row       = [1, 16, 32, 48]
    grade_str        = ["좋음", "보통", "나쁨", "매우나쁨"]
    grade_color      = ["aqua", "lime", "yellow", "orange"]
    week_korean_info = ['월', '화', '수', '목', '금', '토', '일']
    
    # Info Parsing
    ## finedust info parsing 
    pm10value = None
    pm25value = None
    pm10_grade = None
    pm25_grade = None
    if finedust_info["apiSuccess"] == True:
        finedust_info_rst = finedust_info["result"]
        pm10value = finedust_info_rst.get("pm10Value", None)
        pm25value = finedust_info_rst.get("pm25Value", None)
        if pm10value != None:
            pm10value = int(pm10value)
            if pm10value < 31: pm10_grade = 0
            elif pm10value < 81: pm10_grade = 1
            elif pm10value < 151: pm10_grade = 2
            else: pm10_grade = 3
        if pm25value != None:
            pm25value = int(pm25value)
            if pm25value < 16: pm25_grade = 0
            elif pm25value < 36: pm25_grade = 1
            elif pm25value < 76: pm25_grade = 2
            else: pm25_grade = 3
        
    ## temp & weather info parsing
    weather_str = None
    if weather_info['apiSuccess'] == True:
        weather_info_rst = weather_info['result']
        
        weather_tmn = None
        weather_tmx = None
        weather_wts = None
        
        for weather_item in weather_info_rst:
            if weather_item == None:
                break
            
            item_category = weather_item.get('category', None)
            
            if item_category == "TMN":
                weather_tmn = weather_item.get('fcstValue', None)
            elif item_category == "TMX":
                weather_tmx = weather_item.get('fcstValue', None)
            elif item_category == "WTS":
                weather_wts = weather_item.get('fcstValue', None)
            else:
                continue
        
        if weather_tmn != None and weather_tmx != None and weather_wts != None:
            weather_str = f"{str(weather_tmn)[:-2]}~{str(weather_tmx)[:-2]}℃ ({weather_wts})"
        elif weather_tmn != None and weather_tmx != None:
            weather_str = f"{str(weather_tmn)[:-2]}~{str(weather_tmx)[:-2]}℃"
    
    # Show Page
    while True:
        display = Image.new('RGB', matrix_manager.MATRIX_SIZE, "black")
        draw = ImageDraw.Draw(display)
        draw.fontmode = "1"
        
        now = datetime.datetime.now()
        now_fstr = now.strftime(f'%m/%d({week_korean_info[now.weekday()]}) %H시%M분')
        date_align = utils.get_text_align_space(matrix_manager.MATRIX_SIZE[0], now_fstr, config.SCD4_FONT_14)
        draw.text((date_align, y_loca_row[0]), now_fstr, "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[0], y_loca_row[1]), "초미세먼지", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[0], y_loca_row[2]), "미세먼지", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[0], y_loca_row[3]), "내일의날씨", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[1], y_loca_row[1]), ":", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[1], y_loca_row[2]), ":", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[1], y_loca_row[3]), ":", "white", config.SCD4_FONT_14)
        
        ## print pm10, pm25 finedust info
        if pm10_grade != None:
            draw.text((x_loca_col[2], y_loca_row[1]), grade_str[pm10_grade], grade_color[pm10_grade], config.SCD4_FONT_14)
        else:
            draw.text((x_loca_col[2], y_loca_row[1]), "정보없음", "gray", config.SCD4_FONT_14)
        
        if pm25_grade != None:
            draw.text((x_loca_col[2], y_loca_row[2]), grade_str[pm25_grade], grade_color[pm25_grade], config.SCD4_FONT_14)
        else:
            draw.text((x_loca_col[2], y_loca_row[2]), "정보없음", "gray", config.SCD4_FONT_14)
        
        
        ## print weather info
        if weather_str != None:
            draw.text((x_loca_col[2], y_loca_row[3]), f"{weather_str}", "white", config.SCD4_FONT_14)
        else:
            draw.text((x_loca_col[2], y_loca_row[3]), "정보없음", "gray", config.SCD4_FONT_14)
        
        # refresh display
        matrix_manager.refresh(display)
        
        # show time check
        if (datetime.datetime.now() - _start_time).total_seconds() > _show_time_sec:
            break
        time.sleep(0.1)
    
    return 0