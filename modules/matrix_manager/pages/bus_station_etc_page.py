import datetime
import time
from PIL import Image, ImageDraw
import modules.config as config
import modules.utils as utils
import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager

def show_station_etc_page(_show_station_num: int, _show_time_sec: int):
    try:
        station_data = info_manager.service.station_datas[_show_station_num]
    except:
        matrix_manager.matrix_pages.show_text_page([f"실시간 버스 부가정보 화면 [{_show_station_num}]", "잘못된 인덱스입니다. 인덱스 번호를 확인하세요.", "화면을 표시할 수 없습니다.", "", f"{utils.get_now_iso_time()}"], _repeat=1)
        return 1
    
    _start_time = datetime.datetime.now()

    weather_info = station_data['weatherInfo']
    finedust_info = station_data['finedustInfo']
    
    x_loca_col  = [0, 70, 77]
    y_loca_row  = [1, 16, 32, 48]
    w_info      = ['월', '화', '수', '목', '금', '토', '일']
    grade_str   = ["좋음", "보통", "나쁨", "매우나쁨"]
    grade_color = ["aqua", "lime", "yellow", "orange"]
    
    # Info Parsing
    ## finedust info parsing 
    pm10value = None
    pm25value = None
    pm10_grade = None
    pm25_grade = None
    if finedust_info["errorOcrd"] == False and finedust_info["apiSuccess"] == True:
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
    if weather_info["errorOcrd"] == False and weather_info['apiSuccess'] == True:
        weather_str = '정보없음'
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
    
    while True:
        display = Image.new('RGB', matrix_manager.MATRIX_SIZE, "black")
        draw = ImageDraw.Draw(display)
        draw.fontmode = "1"
        
        now = datetime.datetime.now()
        now_fstr = now.strftime(f'%m/%d({w_info[now.weekday()]}) %H시%M분')
        date_align = utils.get_text_align_space(matrix_manager.MATRIX_SIZE[0], now_fstr, config.SCD4_FONT_14)
        draw.text((date_align, y_loca_row[0]), now_fstr, "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[0], y_loca_row[1]), "초미세먼지", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[0], y_loca_row[2]), "미세먼지", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[0], y_loca_row[3]), "내일의날씨", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[1], y_loca_row[1]), ":", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[1], y_loca_row[2]), ":", "white", config.SCD4_FONT_14)
        draw.text((x_loca_col[1], y_loca_row[3]), ":", "white", config.SCD4_FONT_14)
        
        # pm10, pm25 finedust info
        if pm10_grade != None:
            draw.text((x_loca_col[2], y_loca_row[1]), grade_str[pm10_grade], grade_color[pm10_grade], config.SCD4_FONT_14)
        if pm25_grade != None:
            draw.text((x_loca_col[2], y_loca_row[2]), grade_str[pm25_grade], grade_color[pm25_grade], config.SCD4_FONT_14)
            
        draw.text((x_loca_col[2], y_loca_row[3]), f"{weather_str}", "white", config.SCD4_FONT_14)
                
        matrix_manager.refresh(display)
        
        if (datetime.datetime.now() - _start_time).total_seconds() > _show_time_sec:
            break
        
        time.sleep(0.1)
        
    return 0