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
# import rgbmatrix
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except Exception as e:
    sys.exit(f'RGBMatrix module import failed : {e}')
# import everline_api module
try:
    sys.path.append(os.path.join(os.getcwd()))
    from module.everline_api import everline_api
    everline = everline_api.EverlineAPI()
except Exception as e:
    sys.exit(f'everline_api module import failed : {e}')

class MatrixManager:
    def __init__(self, _OPTIONS, _speaker_manager) -> None:
        self.speaker_manager = _speaker_manager
        
        self.load_option(_OPTIONS)
        
        # Configuration for the matrix
        # https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/include/led-matrix.h#L57
        options = RGBMatrixOptions()
        options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
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
        self.matrix = RGBMatrix(options = options)
        
        self.size = (self.matrix.width, self.matrix.height)
        # self.size = (224, 64)
        
        # class var init
        self.station_datas = None
        self.station_data_len = 0
        self.network_connected = False
        
        # font load
        font_path = os.path.join(os.getcwd(), 'src', 'fonts')
        self.font8  = ImageFont.truetype(os.path.join(font_path, 'SCDream4.otf'), 8)
        self.font10 = ImageFont.truetype(os.path.join(font_path, 'SCDream4.otf'), 11)
        self.font12 = ImageFont.truetype(os.path.join(font_path, 'SCDream4.otf'), 12)
        self.font14 = ImageFont.truetype(os.path.join(font_path, 'SCDream4.otf'), 14)
        self.font16 = ImageFont.truetype(os.path.join(font_path, 'SCDream5.otf'), 16)
        self.font26 = ImageFont.truetype(os.path.join(font_path, 'SCDream8.otf'), 26)
        
        # icon load
        icon_path = os.path.join(os.getcwd(), 'src', 'icon')
        self.bus_icon_path = os.path.join(icon_path, 'bus.png')
        self.bus_icon = Image.open(self.bus_icon_path)
        self.bus_lp_icon_path = os.path.join(icon_path, 'bus_lp.png')
        self.bus_lp_icon = Image.open(self.bus_lp_icon_path)
        self.no_wifi_icon_path = os.path.join(icon_path, 'no_wifi.png')
        self.no_wifi_icon = Image.open(self.no_wifi_icon_path)
        
    def load_option(self, _OPTIONS):
        self.OPTIONS = _OPTIONS
        
    def logging(self, str: str, type="info") -> bool:
        if self.OPTION['logging'] == False:
            return False
        
        try:
            self.logger
        except AttributeError:
            self.logger = utils.create_logger('info_manager')
        
        if type == "debug":
            self.logger.debug(str)
        elif type == "info":
            self.logger.info(str)
        elif type == "warning" or type == "warn":
            self.logger.warning(str)
        elif type == "error":
            self.logger.error(str)
        elif type == "critical":
            self.logger.critical(str)
        else:
            self.logger.info(str)
            
        return True
    
    def update_station_info(self, station_datas: dict) -> None:
        self.station_datas = station_datas
        self.station_data_len = len(station_datas)
    
    def get_text_volume(self, text, font) -> int:
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]  # Right - Left
        return text_width
    
    def get_text_align_space(self, _width, _text, _font) -> tuple:
        return int( (_width - self.get_text_volume(_text, _font)) / 2 )
    
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
        
    def error_page(self, error_str, page_time = 3):
        image_path = './src/icon'
        error_icon = Image.open(os.path.join(image_path, 'error_icon.png'))

        canvas = Image.new('RGB', self.size, "black")
        draw = ImageDraw.Draw(canvas)
        draw.fontmode = "1"
        
        for i in range((page_time * 10), 0, -1):
            draw.rectangle([(0, 0), self.size], fill=(0, 0, 0))
            canvas.paste(error_icon, (0, 0))
            draw.text((32, 0), "Error ", fill=(255, 255, 255), font=ImageFont.load_default(16))
            draw.text((32, 16), "System error occurred.", fill=(255, 255, 255), font=ImageFont.load_default(16))
            draw.text((0, 34), error_str, fill=(255, 255, 255), font=ImageFont.load_default(12))
            draw.text((0, 48), f"System will reboot after {i/10}s", fill=(255, 255, 255), font=ImageFont.load_default(12))
            
            self.refresh(canvas, False)
            time.sleep(0.1)
        
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
        try:
            station_data = self.station_datas[_show_station_num]
        except:
            self.show_text_page([f"실시간 버스 정보 화면 [{_show_station_num}]", "잘못된 인덱스입니다. 인덱스 번호를 확인하세요.", "화면을 표시할 수 없습니다.", "", f"{utils.get_now_iso_time()}"], _repeat=1)
            return 1
        
        # # write log
        # with open('./log/first-struct.log', 'w', encoding='UTF-8') as f:
        #     f.write(json.dumps(station_data))
        
        # remain_cnt_grade = ['여유', '보통', '혼잡', '매우혼잡']
        # #                         여유       보통    혼잡    매우혼잡  숫자  미정
        # remain_cnt_grade_color = ['magenta', 'lime', 'yellow', 'red', 'red', 'lime']
        # remain_cnt_number_print_route_type = ['11', '43', '51']
        
        bus_type_color = {
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
        station_info = station_data.get('stationInfo', None)
        station_arvl_bus = station_data.get('arvlBus')
        station_arvl_bus_info = station_data.get('arvlBusInfo')
        station_arvl_bus_route_info = station_data.get('arvlBusRouteInfo')
        
        # station title data parsing
        if station_info['errorOcrd'] == True:
            self.show_text_page([f"실시간 버스 정보 화면 [{_show_station_num}]", "API 오류. 페이지를 표시할 수 없습니다.", "", f"KEYWORD={station_keyword}", f"{station_info.get('errorMsg', '알 수 없는 오류입니다.')}"], _repeat=2)
            return 1
        if station_info.get('apiSuccess') == False:
            rst_code = station_info.get('rstCode', "-1")
            rst_msg = station_info.get('rstMsg', "알 수 없는 오류입니다.")
            self.show_text_page([f"실시간 버스 정보 화면 [{_show_station_num}]", "데이터 오류. 페이지를 표시할 수 없습니다: 필수 데이터가 없습니다.", "", f"KEYWORD={station_keyword}", f"({rst_code}) {rst_msg}"], _repeat=2)
            return 1
        
        station_title = f"{station_info['result'].get('stationName', '')}"
        if station_info['result'].get('mobileNo', None) != None:
            station_title += f" [{station_info['result']['mobileNo']}]"
        if station_desc != None:
            station_title += f" {station_desc}"
            
        # arvl bus data parsing
        arvl_bus_infos = []
        if station_arvl_bus.get('apiSuccess') == True:
            for index, arvl_bus in enumerate(station_arvl_bus['result']):
                bus_info = arvl_bus
                
                # arvl bus info parsing
                arvl_bus_info = station_arvl_bus_info[index]
                if arvl_bus_info.get('apiSuccess', False):
                    bus_info.update(arvl_bus_info.get('result'))
                
                arvl_bus_route_info = station_arvl_bus_route_info[index]
                if arvl_bus_route_info.get('apiSuccess', False):
                    bus_info.update({"route_list": arvl_bus_route_info.get('result')})
                
                # adding bus info 
                ## isArvl check
                if int(arvl_bus.get('locationNo1')) <= 3:
                    arvl_bus['isArvl'] = True
                else:
                    arvl_bus['isArvl'] = False
                
                ## bus Now station info parsing
                if arvl_bus.get('route_list', None) != None and arvl_bus.get('staOrder', None) != None and arvl_bus.get('locationNo1', None) != None:
                    bus_now_station_info = arvl_bus['route_list'][(int(arvl_bus['staOrder'])-1) - int(arvl_bus['locationNo1'])]
                    bus_info.update({"nowStationId" : bus_now_station_info.get('stationId', None)})
                    bus_info.update({"nowStationName" : bus_now_station_info.get('stationName', None)})
                
                ## remain seat grade parsing
                if arvl_bus.get('remainSeatCnt1', '-1') == '-1':
                    arvl_bus_remainSeatGrade = '--'
                    arvl_bus_remainSeatGradeColor = 'dimgray'
                else:
                    arvl_bus_remainSeatGrade = f"({arvl_bus.get('remainSeatCnt1', '-1')})"
                    arvl_bus_remainSeatGradeColor = bus_type_color.get(arvl_bus.get('routeTypeCd', None), 'white')
                bus_info.update({"remainSeatGrade" : arvl_bus_remainSeatGrade})
                bus_info.update({"remainSeatGradeColor" : arvl_bus_remainSeatGradeColor})
                
                arvl_bus_infos.append(bus_info)
            arvl_bus_infos = sorted(arvl_bus_infos, key=lambda info: int(info["predictTime1"]))
            
        # no arvl bus
        else:
            pass
        
        x_loca = [0, 10, 63, 93, 130]
        y_loca = [0, 13, 26, 39, 52]
        x_loca_bus_arvl = [0, 40]
        
        arvl_str_infos = {
            "text": "",
            "x_loca": x_loca_bus_arvl[1],
            "overflow": False,
            "frame_cnt": 0,
            "mv_cnt": 0
        }
        
        arvl_infos = []
        normal_infos = []
        for arvl_bus_info in arvl_bus_infos:
            if arvl_bus_info.get('isArvl', False) == True:
                if arvl_bus_info.get('remainSeatCnt1', '-1') == '-1':
                    arvl_str_infos['text'] += f"{arvl_bus_info.get('routeName', '')}, "
                else:
                    arvl_str_infos['text'] += f"{arvl_bus_info.get('routeName', '')}({arvl_bus_info.get('remainSeatCnt1', '')}), "
                arvl_infos.append(arvl_bus_info)
            else:
                normal_infos.append(arvl_bus_info)
        if arvl_str_infos['text'] != "":
            arvl_str_infos['text'] = arvl_str_infos['text'][:-2]
        
        arvl_str_infos['of_size'] = self.get_text_volume(arvl_str_infos['text'], self.font12) - (self.size[0] - x_loca_bus_arvl[1])
        if arvl_str_infos['of_size'] > 0:
            arvl_str_infos['overflow'] = True
        
        # create display
        display = Image.new('RGB', self.size, "black")
        draw = ImageDraw.Draw(display)
        draw.fontmode = "1"
        
        station_title_align = self.get_text_align_space(self.size[0], station_title, self.font12)
        station_title_info = {
            'text': station_title,
            'x_loca': station_title_align,
            'overflow': False,
            'frame_cnt': 0,
            'mv_cnt': 0
        }
        if self.get_text_volume(station_title, self.font12) > self.size[0]:
            station_title_info['overflow'] = True
            station_title_info['x_loca'] = 0
            station_title_info['of_size'] = self.get_text_volume(station_title, self.font12) - self.size[0]
        draw.text((station_title_info['x_loca'], y_loca[0]), station_title, "white", self.font12)
        
        for bus_data_list in utils.chunk_list(normal_infos):
            arvl_bus_end_mv_cnt = None
            station_title_end_mv_cnt = None
            
            arvl_bus_now_station_str_infos = [];
            bus_now_station_str_width = self.size[0] - x_loca[4]
            for index, bus_dict in enumerate(bus_data_list):
                # default value
                arvl_bus_now_station_str_info = {
                    'text': bus_dict.get('nowStationName', ''),
                    'overflow': False,
                    'x_loca': x_loca[4]
                }
                
                # check overflow
                if bus_now_station_str_width < self.get_text_volume(bus_dict.get('nowStationName', ''), self.font12):
                    arvl_bus_now_station_str_info['overflow'] = True
                    arvl_bus_now_station_str_info['text'] = f"{arvl_bus_now_station_str_info['text']} " * 3
                
                arvl_bus_now_station_str_infos.append(arvl_bus_now_station_str_info)
        
            for frame in range(0, 200):
                # station title이 overflow일 경우
                station_title_info['frame_cnt'] += 1
                if station_title_info['frame_cnt'] >= 39 and station_title_info['overflow']:
                    if frame % 2 == 1:
                        if station_title_info['mv_cnt'] < station_title_info['of_size']:
                            station_title_info['x_loca'] -= 1
                            station_title_info['mv_cnt'] += 1
                        else:
                            if station_title_end_mv_cnt == None:
                                station_title_end_mv_cnt = 40
                            else:
                                station_title_end_mv_cnt -= 1
                                if station_title_end_mv_cnt == 0:
                                    station_title_info['frame_cnt'] = 0
                                    station_title_info['mv_cnt'] = 0
                                    station_title_info['x_loca'] = 0
                                    station_title_end_mv_cnt = None
                        draw.rectangle([(0, y_loca[0]), (self.size[0], y_loca[1]-1)], fill="black")
                        draw.text((station_title_info['x_loca'], y_loca[0]), station_title_info['text'], "white", self.font12)
                        
                draw.rectangle([(0, y_loca[1]), (self.size[0], y_loca[4]-1)], fill="black")
                for index, bus_dict in enumerate(bus_data_list):
                    if frame >= 40 and arvl_bus_now_station_str_infos[index]['overflow']:
                        arvl_bus_now_station_str_infos[index]['x_loca'] -= 1
                    
                    bus_routeTypeCd = bus_dict.get("routeTypeCd", "-1")
                    
                    # 5 print bus arvl station
                    draw.text((arvl_bus_now_station_str_infos[index]['x_loca'], y_loca[index+1]), arvl_bus_now_station_str_infos[index]['text'], "white", self.font12)
                    draw.rectangle((x_loca[0], y_loca[index+1], x_loca[4]-1, y_loca[index+2]-1), fill="black")
                    
                    # 1 print bus icon
                    draw.bitmap((x_loca[0], y_loca[index+1]), self.bus_icon, bus_type_color.get(bus_routeTypeCd, "white"));
                    
                    # 2 print route name
                    draw.text((x_loca[1], y_loca[index+1]), bus_dict.get('routeName', ''), "white", self.font12)
                    
                    # 3 print remain seat grade
                    remain_seat_str_align_val = self.get_text_align_space(x_loca[3]-x_loca[2], bus_dict.get('remainSeatGrade'), self.font12)
                    draw.text((x_loca[2]+remain_seat_str_align_val, y_loca[index+1]), bus_dict.get('remainSeatGrade'), bus_dict.get('remainSeatGradeColor'), self.font12)
                    
                    # 4 print predict time
                    predict_time_str_align_val = self.get_text_align_space(x_loca[4]-x_loca[3], f"{bus_dict.get('predictTime1', '')}분", self.font12)
                    draw.text((x_loca[3]+predict_time_str_align_val, y_loca[index+1]), f"{bus_dict.get('predictTime1', '')}분", "aqua", self.font12)
                
                # 2 print arvl bus str
                draw.rectangle(((x_loca_bus_arvl[1], y_loca[4]), (self.size[0], self.size[1])), fill="black")
                draw.text((arvl_str_infos['x_loca'], y_loca[4]), arvl_str_infos['text'], "white", self.font12)
                
                # 1 print arvl bus title
                draw.rectangle(((0, y_loca[4]), (x_loca_bus_arvl[1]-1, self.size[1])), fill="black")
                draw.text((x_loca_bus_arvl[0], y_loca[4]), "곧도착:", "white", self.font12)
                
                arvl_str_infos['frame_cnt'] += 1
                if arvl_str_infos['frame_cnt'] >= 39 and arvl_str_infos['overflow']:
                    if frame % 2 == 1:
                        if not (arvl_str_infos['mv_cnt'] >= arvl_str_infos['of_size']):
                            arvl_str_infos['x_loca'] -= 1
                            arvl_str_infos['mv_cnt'] += 1
                        else:
                            if arvl_bus_end_mv_cnt == None:
                                arvl_bus_end_mv_cnt = 40
                            else:
                                arvl_bus_end_mv_cnt -= 1
                                if arvl_bus_end_mv_cnt == 0:
                                    arvl_str_infos['frame_cnt'] = 0
                                    arvl_str_infos['mv_cnt'] = 0
                                    arvl_str_infos['x_loca'] = x_loca_bus_arvl[1]
                                    arvl_bus_end_mv_cnt = None
                
                self.refresh(display)
                time.sleep(0.02)
    
    def show_station_etc_page(self, _show_station_num: int, _repeat: int = 50):
        try:
            station_data = self.station_datas[_show_station_num]
        except:
            self.show_text_page([f"실시간 버스 부가정보 화면 [{_show_station_num}]", "잘못된 인덱스입니다. 인덱스 번호를 확인하세요.", "화면을 표시할 수 없습니다.", "", f"{utils.get_now_iso_time()}"], _repeat=1)
            return 1

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
        
        # create display
        for i in range(0, _repeat):
            display = Image.new('RGB', self.size, "black")
            draw = ImageDraw.Draw(display)
            draw.fontmode = "1"
            
            now = datetime.datetime.now()
            now_fstr = now.strftime(f'%m/%d({w_info[now.weekday()]}) %H시%M분')
            date_align = self.get_text_align_space(self.size[0], now_fstr, self.font14)
            draw.text((date_align, y_loca_row[0]), now_fstr, "white", self.font14)
            draw.text((x_loca_col[0], y_loca_row[1]), "초미세먼지", "white", self.font14)
            draw.text((x_loca_col[0], y_loca_row[2]), "미세먼지", "white", self.font14)
            draw.text((x_loca_col[0], y_loca_row[3]), "내일의날씨", "white", self.font14)
            draw.text((x_loca_col[1], y_loca_row[1]), ":", "white", self.font14)
            draw.text((x_loca_col[1], y_loca_row[2]), ":", "white", self.font14)
            draw.text((x_loca_col[1], y_loca_row[3]), ":", "white", self.font14)
            
            # pm10, pm25 finedust info
            if pm10_grade != None:
                draw.text((x_loca_col[2], y_loca_row[1]), grade_str[pm10_grade], grade_color[pm10_grade], self.font14)
            if pm25_grade != None:
                draw.text((x_loca_col[2], y_loca_row[2]), grade_str[pm25_grade], grade_color[pm25_grade], self.font14)
            
                
                draw.text((x_loca_col[2], y_loca_row[3]), f"{weather_str}", "white", self.font14)
                    
            self.refresh(display)
            time.sleep(0.1)
            
        self.refresh(display)
        time.sleep(1)
        return 0
    
    def show_everline_page(self, _show_time_sec: int = 15):
        image_path = './src/icon'
        ev_options = self.OPTIONS['everline']
        station_icon = Image.open(os.path.join(image_path, 'everline_station.png')).convert("RGBA")
        train_icon = Image.open(os.path.join(image_path, 'everline_train.png')).convert("RGBA")
        reverse_train_icon = train_icon.transpose(Image.FLIP_LEFT_RIGHT)
        font_path = os.path.join(os.getcwd(), 'src', 'fonts')
        font8  = ImageFont.truetype(os.path.join(font_path, 'SCDream5.otf'), 8)
        font10 = ImageFont.truetype(os.path.join(font_path, 'SCDream5.otf'), 10)
        font11 = ImageFont.truetype(os.path.join(font_path, 'SCDream4.otf'), 11)

        RECTANGLE_TOP = 30

        # Calculate positions to center the icon within the rectangle and at 20 pixels from left and right
        center_x = (self.size[0] - station_icon.width) // 2
        center_y = RECTANGLE_TOP + (RECTANGLE_TOP+4 - RECTANGLE_TOP - station_icon.height) // 2
        left_x = 5
        right_x = 206
        train_center_x = 102
        train_back_x = 2
        train_next_x = 202

        # Draw Image
        canvas = Image.new('RGBA', self.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.fontmode = "1"
        
        back_station = ev_options['backStation']
        base_station = ev_options['baseStation']
        next_station = ev_options['nextStation']
        everline.auto_update(ev_options['refreshInterval'])
        
        station_title = f"[에버라인 운행정보] {everline_api.STATION_CODE[base_station]}역"
        title_bbox = font11.getbbox(station_title)
        title_width = title_bbox[2] - title_bbox[0]
        station_title_center = (self.size[0] - title_width) // 2
        
        train_x = -20
        start_time = time.time()
        while True:
            if time.time() - start_time > _show_time_sec:
                break
            
            now_hhmm = datetime.datetime.now().strftime('%H%M')
            title_now_hhmm = datetime.datetime.now().strftime('%H:%M')
            train_infos = everline.get_train_info()
            
            draw.rectangle([(0, 0), self.size], fill=(0, 0, 0, 0))
            draw.text((station_title_center, 0), station_title, fill=(255, 255, 255), font=font11)
            draw.text((195, 0), f"{title_now_hhmm}", fill=(150, 150, 150), font=ImageFont.load_default(size=10))
            draw.line([(0, RECTANGLE_TOP+1), (self.size[0], RECTANGLE_TOP+1)], fill=(100, 100, 100, 255), width=5)
            
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
                draw.text((0, self.size[1]-11), f"열차는 매 {train_interval}분마다 운행합니다.", fill=(255, 255, 255, 255), font=font10)
            else:
                draw.text((0, self.size[1]-11), "열차가 운행하지 않는 시각입니다.", fill=(255, 255, 255, 255), font=font10)
                
            self.refresh(canvas.convert("RGB"))
            time.sleep(0.01)
            train_x += 1
            if train_x > self.size[0]:
                train_x = -20
    
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
        
        # display.save('./display.png')
        self.matrix.SetImage(display.convert('RGB'))