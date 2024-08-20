import json
import os
import sys
import time
import datetime

# import pillow
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:
    sys.exit(f'pillow module import failed. {e}\n')
# import module.utils
try:
    import module.utils as utils
except Exception as e:
    sys.exit(f'module.utils module import failed : {e}')
# # import rgbmatrix
# try:
#     from rgbmatrix import RGBMatrix, RGBMatrixOptions
# except Exception as e:
#     sys.exit(f'RGBMatrix module import failed : {e}')

class MatrixManager:
    def __init__(self, station_datas: dict | None = []) -> None:
        # # Configuration for the matrix
        # # https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/include/led-matrix.h#L57
        # options = RGBMatrixOptions()
        # options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
        # options.rows = 32
        # options.cols = 64
        # options.chain_length = 7
        # # https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/examples-api-use#remapping-coordinates
        # options.pixel_mapper_config = "V-mapper;Rotate:90"
        # options.pwm_lsb_nanoseconds = 50
        # options.gpio_slowdown = 4
        # options.pwm_bits = 5
        # options.pwm_dither_bits = 0
        # options.show_refresh_rate = False
        # self.matrix = RGBMatrix(options = options)
        
        # self.size = (self.matrix.width, self.matrix.height)
        self.size = (224, 64)
        
        # class var init
        self.station_datas = station_datas
        self.station_data_len = 0
        self.network_connected = False
        
        # font load
        self.font8  = ImageFont.truetype(os.path.join('fonts', 'SCDream4.otf'), 8)
        self.font10 = ImageFont.truetype(os.path.join('fonts', 'SCDream4.otf'), 11)
        self.font12 = ImageFont.truetype(os.path.join('fonts', 'SCDream4.otf'), 12)
        self.font14 = ImageFont.truetype(os.path.join('fonts', 'SCDream4.otf'), 14)
        self.font14b = ImageFont.truetype(os.path.join('fonts', 'SCDream5.otf'), 14)
        self.font16 = ImageFont.truetype(os.path.join('fonts', 'SCDream5.otf'), 16)
        self.font26 = ImageFont.truetype(os.path.join('fonts', 'SCDream8.otf'), 26)
        
        # icon load
        self.bus_icon_path = os.path.join('src', 'icon', 'bus.png')
        self.bus_icon = Image.open(self.bus_icon_path)
        self.bus_lp_icon_path = os.path.join('src', 'icon', 'bus_lp.png')
        self.bus_lp_icon = Image.open(self.bus_lp_icon_path)
        self.no_wifi_icon_path = os.path.join('src', 'icon', 'no_wifi.png')
        self.no_wifi_icon = Image.open(self.no_wifi_icon_path)
        
        
    def update_station_info(self, station_datas: dict) -> None:
        self.station_datas = station_datas
        self.station_data_len = len(station_datas)
    
    def check_internet_connection(self) -> bool:
        try:
            utils.check_internet_connection()
            self.network_connected = True
            return True
        except:
            self.network_connected = False
            return False
    
    def get_text_volume(self, text, font) -> int:
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]  # Right - Left
        return text_width
    
    def get_text_align_space(self, _text, _font) -> tuple:
        return int( (self.size[0] - self.get_text_volume(_text, _font)) / 2 )
    
    def show_test_page(self, _test_type: int = 0, _delay_time:int = 1):
        display = Image.new('RGB', self.size, color = 'black')
        draw = ImageDraw.Draw(display)
        test_color = ["red", "lime", "blue", "white"]
        if _test_type == 0:
            for color in test_color:
                draw.rectangle(((0, 0), (self.size[0], self.size[1])), color)
                self.refresh(display, status_prt=False)
                time.sleep(_delay_time)
        elif _test_type == 1:
            for i in range(0, self.size[0]):
                for j in range(0, self.size[1]):
                    draw.point((i, j), test_color[(i+j) % 4])
                self.refresh(display, status_prt=False)
                time.sleep(0.01)
            time.sleep(_delay_time)
        elif _test_type == 2:
            for y in range(0, self.size[1], 7):
                draw.line((0, y, self.size[0], y), fill='white')
            for x in range(0, self.size[0], 9):
                draw.line((x, 0, x, self.size[1]), fill='white')
            self.refresh(display, status_prt=False)
            time.sleep(_delay_time)
        draw.rectangle(((0, 0), (self.size[0], self.size[1])), "black")
        self.refresh(display, status_prt=False)
        
    def show_text_page(self, _set_text: str | list = "", _first_show_time: int | float = 1, _end_show_time: int | float = 1, _repeat: int = 1, _status_prt: bool = True):
        if isinstance(_set_text, str):
            texts = [_set_text]
        elif isinstance(_set_text, list):
            texts = _set_text

        text_widths = [self.get_text_volume(text, self.font12) for text in texts]
        display_width = self.size[0]

        canvas = Image.new('RGB', self.size, "black")
        draw = ImageDraw.Draw(canvas)
        draw.fontmode = "1"

        for repeat in range(_repeat):
            for i, text in enumerate(texts):
                x_loca_row = [0, 13, 26, 39, 51]
                if i < len(x_loca_row):
                    draw.text((1, x_loca_row[i]), str(text), "white", self.font12)

            self.refresh(canvas, status_prt=_status_prt)
            time.sleep(_first_show_time)

            moving_texts = [text for text, width in zip(texts, text_widths) if width > display_width]
            initial_positions = {text: self.size[0] for text in moving_texts}

            if not moving_texts:
                time.sleep(_end_show_time)
                if isinstance(_set_text, list) and ( len(_set_text) > 5 ):
                    self.show_text_page(_set_text[5:], _first_show_time, _end_show_time)
                return 0

            while True:
                canvas = Image.new('RGB', self.size, "black")
                draw = ImageDraw.Draw(canvas)
                draw.fontmode = "1"

                all_texts_moved = True
                for i, text in enumerate(texts):
                    if text in moving_texts:
                        position_x = initial_positions[text]
                        if position_x + self.get_text_volume(text, self.font12) > 0:
                            draw.text((position_x, i * 13), str(text), "white", self.font12)
                            all_texts_moved = False
                    else:
                        x_loca_row = [0, 13, 26, 39, 51]
                        if i < len(x_loca_row):
                            draw.text((1, x_loca_row[i]), str(text), "white", self.font12)

                self.refresh(canvas, status_prt=_status_prt)

                time.sleep(0.01)

                for text in moving_texts:
                    initial_positions[text] -= 1

                if all_texts_moved:
                    time.sleep(_end_show_time)
                    break
        
        if isinstance(_set_text, list) and ( len(_set_text) > 5 ):
            self.show_text_page(_set_text[5:], _first_show_time, _end_show_time, _repeat)
        
        return 0
    
    def show_station_page(self, _show_station_num: int):        
        station_data = self.station_datas[_show_station_num]
        with open('./log/struct.log', 'w', encoding='UTF-8') as f:
            f.write(json.dumps(station_data))
        
        remain_cnt_grade = ['여유', '보통', '혼잡', '매우혼잡']
        #                         여유       보통    혼잡    매우혼잡  숫자  미정
        remain_cnt_grade_color = ['magenta', 'lime', 'yellow', 'red', 'red', 'lime']
        remain_cnt_number_print_route_type = ['11', '43', '51']
        
        bus_icon_color = {
            None : "white",       # 모를 때
            "-1" : "white",       
            "11" : "red",         # 직행좌석형시내버스 (5001, 5005)
            "13" : "lime",        # 일반형시내버스 (66-4, 10)
            "14" : "red",         # 광역급행형시내버스
            "30" : "yellow",      # 마을버스 (5)
            "43" : "darkviolet",  # 시외버스(8342, 8343)
            "51" : "sienna"       # 리무진공항버스(8165)
        }
        
        station_keyword = station_data.get('keyword', '읽기실패')
        station_desc = station_data.get('stationDesc', None)
        station_info = station_data.get('stationInfo', {'apiSuccess': False})
        station_arvl_bus = station_data.get('arvlBus', {'apiSuccess': False})
        station_arvl_bus_info = station_data.get('arvlBusInfo', {'apiSuccess': False})
        station_arvl_bus_route_info = station_data.get('arvlBusRouteInfo', {'apiSuccess': False})
        
        # station title data parsing
        if station_info == None or station_info.get('apiSuccess') == False:
            rst_code = station_info.get('rstCode', "-1")
            rst_msg = station_info.get('rstMsg', "알 수 없는 오류입니다.")
            self.show_text_page([f"스테이션 페이지 [{_show_station_num}]", "데이터 오류. 페이지를 표시할 수 없습니다: 필수 데이터가 없습니다.", "", f"KEYWORD={station_keyword}", f"({rst_code}) {rst_msg}"], _repeat=2)
            return 1
        
        station_title = f"{station_info['result'].get('stationName', '역이름이없습니다')}"
        if station_info['result'].get('mobileNo', None) != None: station_title += f" [{station_info['result']['mobileNo']}]"
        if station_desc != None: station_title += f" {station_desc}"
        station_align = self.get_text_align_space(station_title, self.font12)
        
        # arvl bus data parsing
        arvl_bus_infos = []
        if station_arvl_bus.get('apiSuccess') == True:
            for i in range(0, len(station_arvl_bus.get('result'))):
                bus_info = {}
                
                # arvl bus parsing
                if station_arvl_bus.get('apiSuccess', False) == True:
                    arvl_bus = station_arvl_bus.get('result', None)
                    if arvl_bus == None or arvl_bus == []:
                        arvl_bus_infos.append(None)
                        continue
                    arvl_bus = arvl_bus[i]
                    bus_info.update(arvl_bus)

                # arvl bus info parsing
                if (station_arvl_bus_info == None or station_arvl_bus_info == []) == False:
                    arvl_bus_info = station_arvl_bus_info[i]
                    if ((arvl_bus_info == None) or (arvl_bus_info.get('apiSuccess', False) == False)) == False:
                        arvl_bus_info = arvl_bus_info.get('result', None)
                        if arvl_bus_info.get('locationNo1', None) != None:
                            if arvl_bus_info['locationNo1'] <= 3:
                                bus_info.update({'isArvl' : True})
                            else:
                                bus_info.update({'isArvl' : False})
                        else:
                            bus_info.update({'isArvl' : False})
                        bus_info.update(arvl_bus_info)
                
                # arvl bus route info parsing
                if (station_arvl_bus_route_info == None or station_arvl_bus_route_info == []) == False:
                    arvl_bus_route_info = station_arvl_bus_route_info[i]
                    if ((arvl_bus_route_info == None) or (arvl_bus_route_info.get('apiSuccess', False) == False)) == False:
                        arvl_bus_route_info = arvl_bus_route_info.get('result', None)
                        arvl_bus_staOrder = bus_info.get('staOrder', None)
                        arvl_bus_locationNo1 = bus_info.get('locationNo1', None)
                        if arvl_bus_route_info != None and arvl_bus_staOrder != None and arvl_bus_locationNo1 != None:
                            bus_now_station_info = arvl_bus_route_info[(int(arvl_bus_staOrder)-1) - int(arvl_bus_locationNo1)]
                            bus_info.update({"nowStationId" : bus_now_station_info.get('stationId', None)})
                            bus_info.update({"nowStationName" : bus_now_station_info.get('stationName', None)})
                
                arvl_bus_remainSeatCnt1 = bus_info.get('remainSeatCnt1', '-1')
                arvl_bus_routeTypeCd = bus_info.get('routeTypeCd', None)
                # remain seat grade parsing
                ## 정보 없음
                if arvl_bus_remainSeatCnt1 == '-1':
                    arvl_bus_remainSeatGrade = ''
                    arvl_bus_remainSeatGradeColor = remain_cnt_grade_color[5]
                ## 정보 있음
                else:
                    if arvl_bus_routeTypeCd == '':
                        arvl_bus_remainSeatGrade = f"({arvl_bus_remainSeatCnt1})"
                        arvl_bus_remainSeatGradeColor = remain_cnt_grade_color[5]
                    elif arvl_bus_routeTypeCd in remain_cnt_number_print_route_type:
                        arvl_bus_remainSeatGrade = f"({arvl_bus_remainSeatCnt1})"
                        arvl_bus_remainSeatGradeColor = remain_cnt_grade_color[4]
                    else:
                        #          대형버스 중형버스 소형버스
                        # 여유     25명이하 20명이하 10명이하
                        # 보통     26~40명  21~35명  11~20명
                        # 혼잡     41~55명  36~50명  21~25명
                        # 매우혼잡 56명이상 51명이상 26명이상
                        if int(arvl_bus_remainSeatCnt1) <= 10:
                            arvl_bus_remainSeatGrade = remain_cnt_grade[0]
                            arvl_bus_remainSeatGradeColor = remain_cnt_grade_color[0]
                        elif int(arvl_bus_remainSeatCnt1) <= 20:
                            arvl_bus_remainSeatGrade = remain_cnt_grade[1]
                            arvl_bus_remainSeatGradeColor = remain_cnt_grade_color[1]
                        elif int(arvl_bus_remainSeatCnt1) <= 25:
                            arvl_bus_remainSeatGrade = remain_cnt_grade[2]
                            arvl_bus_remainSeatGradeColor = remain_cnt_grade_color[2]
                        else:
                            arvl_bus_remainSeatGrade = remain_cnt_grade[3]
                            arvl_bus_remainSeatGradeColor = remain_cnt_grade_color[3]
                
                bus_info.update({"remainSeatGrade": arvl_bus_remainSeatGrade})
                bus_info.update({"remainSeatGradeColor": arvl_bus_remainSeatGradeColor})
                arvl_bus_infos.append(bus_info)
        
        print(f"ASDLASMLDSAD: {arvl_bus_infos}")
        
        # create display
        display = Image.new('RGB', self.size, "black")
        draw = ImageDraw.Draw(display)
        draw.fontmode = "1"
        
        x_loca_col = [0, 10, 63, 93, 130]
        y_loca_row = [0, 13, 26, 39, 52]
        x_loca_col_bus_arvl = [0, 40, 40]
        
        draw.text((station_align, y_loca_row[0]), station_title, "white", self.font12)
        
        arvl_bus_infos = sorted(arvl_bus_infos, key=lambda info: int(info["predictTime1"]))
        
        arvl_infos = []
        arvl_str = ""
        normal_infos = []
        for arvl_bus_info in arvl_bus_infos:
            if arvl_bus_info.get('isArvl', False) == True:
                arvl_str += f"{arvl_bus_info.get('routeName', '')} "
                arvl_infos.append(arvl_bus_info)
            else:
                normal_infos.append(arvl_bus_info)
        
        
        for bus_dict_list in utils.chunk_list(normal_infos):
            for frame in range(0, 120):
                draw.rectangle([(0, y_loca_row[1]), (self.size[0], y_loca_row[4]-1)], outline="black", fill="black")
                for index, bus_dict in enumerate(bus_dict_list):
                    bus_routeTypeCd = bus_dict.get("routeTypeCd", "-1")
                    
                    draw.bitmap((x_loca_col[0], y_loca_row[index+1]), self.bus_icon, bus_icon_color.get(bus_routeTypeCd, "white"));
                    draw.text((x_loca_col[1], y_loca_row[index+1]), bus_dict.get('routeName', ''), "white", self.font12)
                    draw.text((x_loca_col[2], y_loca_row[index+1]), bus_dict.get('remainSeatGrade'), bus_dict.get('remainSeatGradeColor'), self.font12)
                    draw.text((x_loca_col[3], y_loca_row[index+1]), f"{bus_dict.get('predictTime1', '')}분", "white", self.font12)
                    draw.text((x_loca_col[4], y_loca_row[index+1]), f"{bus_dict.get('nowStationName', '')}", "white", self.font12)
                    
                    draw.text((x_loca_col_bus_arvl[0], y_loca_row[4]), "곧도착:", "white", self.font12)
                    draw.text((x_loca_col_bus_arvl[1], y_loca_row[4]), arvl_str, "white", self.font12)
                    
                    self.refresh(display)
                time.sleep(0.05)
        
        
    
    def show_station_etc_page(self, _show_station_num: int, _repeat: int = 50):
        station_data = self.station_datas[_show_station_num]
        station_weather_info = station_data.get('weatherInfo', {'apiSuccess': False})
        if station_weather_info == None: station_weather_info = {'apiSuccess': False}
        station_finedust_info = station_data.get('finedustInfo', {'apiSuccess': False})
        if station_finedust_info == None: station_finedust_info = {'apiSuccess': False}
        
        x_loca_col  = [0, 70, 77]
        y_loca_row  = [1, 16, 32, 48]
        w_info      = ['월', '화', '수', '목', '금', '토', '일']
        grade_str   = ["좋음", "보통", "나쁨", "매우나쁨"]
        grade_color = ["aqua", "lime", "yellow", "orange"]
        
        # finedust info parsing 
        pm10value = None
        pm25value = None
        
        pm10_grade = None
        pm25_grade = None
        if station_finedust_info != None:
            if station_finedust_info.get("apiSuccess", False) == True:
                pm10value = station_finedust_info.get("result").get("pm10Value", None)
                pm25value = station_finedust_info.get("result").get("pm25Value", None)
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
        
        # create display
        for i in range(0, _repeat):
            display = Image.new('RGB', self.size, "black")
            draw = ImageDraw.Draw(display)
            draw.fontmode = "1"
            
            now = datetime.datetime.now()
            now_fstr = now.strftime(f'%m/%d({w_info[now.weekday()]}) %H시%M분')
            date_align = self.get_text_align_space(now_fstr, self.font14b)
            draw.text((date_align, y_loca_row[0]), now_fstr, "white", self.font14b)
            draw.text((x_loca_col[0], y_loca_row[1]), "초미세먼지", "white", self.font14b)
            draw.text((x_loca_col[0], y_loca_row[2]), "미세먼지", "white", self.font14b)
            draw.text((x_loca_col[0], y_loca_row[3]), "내일의날씨", "white", self.font14b)
            draw.text((x_loca_col[1], y_loca_row[1]), ":", "white", self.font14b)
            draw.text((x_loca_col[1], y_loca_row[2]), ":", "white", self.font14b)
            draw.text((x_loca_col[1], y_loca_row[3]), ":", "white", self.font14b)
            
            # pm10, pm25 finedust info
            if pm10_grade != None:
                draw.text((x_loca_col[2], y_loca_row[1]), grade_str[pm10_grade], grade_color[pm10_grade], self.font14b)
            if pm25_grade != None:
                draw.text((x_loca_col[2], y_loca_row[2]), grade_str[pm25_grade], grade_color[pm25_grade], self.font14b)
            
            if station_weather_info.get('apiSuccess', False) == True:
                weather_str = '정보없음'
                weather_info = station_weather_info.get('result', None)
                if weather_info != None:
                    weather_tmn = None
                    weather_tmx = None
                    weather_wts = None
                    
                    for weather_item in weather_info:
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
                        weather_str = f"{weather_tmn}~{weather_tmx}℃ {weather_wts}"
                    elif weather_tmn != None and weather_tmx != None:
                        weather_str = f"{weather_tmn}~{weather_tmx}℃"
                
                draw.text((x_loca_col[2], y_loca_row[3]), f"{weather_str}", "white", self.font14b)
                    

            self.refresh(display)
            time.sleep(0.1)
            
        
        self.refresh(display)
        print("FUNC END")
        time.sleep(1)
        return 0
        
    def duk_50th_anniversary_page(self):
        for i in range(1, -460, -1):
            text = [
                "덕영고 50주년!!",
                "50년의 빛나는 역사, 미래를 향한 무궁한 발전을 기원합니다."
            ]
            
            canvas = Image.new('RGB', self.size, "black")
            draw = ImageDraw.Draw(canvas)
            draw.fontmode="1"
            
            draw.text((1, 1), text[0], "white", self.font26)
            draw.text((i, 32), text[1], "white", self.font26)
            
            self.refresh(canvas)
            
            if i == 1:
                time.sleep(1)
            time.sleep(0.005)
        time.sleep(1.5)
    
    def refresh(self, display, status_prt: bool = True):
        # network status print
        if ((self.network_connected == False) and (status_prt == True)):
            set_loca = [125, 35]
            draw = ImageDraw.Draw(display)
            draw.fontmode="1"
            draw.rectangle([(set_loca[0], set_loca[1]), (set_loca[0]+95, set_loca[1]+25)], outline="white", fill="black")
            draw.bitmap((set_loca[0]+1, set_loca[1]+1),  self.no_wifi_icon, "red");
            draw.text((set_loca[0]+25, set_loca[1]+2), "인터넷 연결을", "white", self.font10)
            draw.text((set_loca[0]+25 , set_loca[1]+13), "확인해주세요.", "white", self.font10)
        
        display.save('./display.png')
        # self.matrix.SetImage(display.convert('RGB'))