import time
from PIL import Image, ImageDraw, ImageFont
import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager
import modules.utils as utils
import modules.config as config

def show_station_page(_show_station_num: int):
    try:
        station_data = info_manager.service.station_datas[_show_station_num]
    except:
        matrix_manager.matrix_pages.text_page(
            [
                f"[ 실시간 버스 정보 화면 ]",
                f"역 정보가 잘못 선택되었습니다.",
                f"화면을 표시할 수 없습니다. 입력된 정보({_show_station_num})를 확인하십시오.",
                f"",
                f"{utils.get_now_iso_time()}"
            ]
            , _repeat=1)
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
        matrix_manager.matrix_pages.show_text_page([f"실시간 버스 정보 화면 [{_show_station_num}]", "API 오류. 페이지를 표시할 수 없습니다.", "", f"KEYWORD={station_keyword}", f"{station_info.get('errorMsg', '알 수 없는 오류입니다.')}"], _repeat=2)
        return 1
    if station_info.get('apiSuccess') == False:
        rst_code = station_info.get('rstCode', "-1")
        rst_msg = station_info.get('rstMsg', "알 수 없는 오류입니다.")
        matrix_manager.matrix_pages.show_text_page([f"실시간 버스 정보 화면 [{_show_station_num}]", "데이터 오류. 페이지를 표시할 수 없습니다: 필수 데이터가 없습니다.", "", f"KEYWORD={station_keyword}", f"({rst_code}) {rst_msg}"], _repeat=2)
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
    
    arvl_str_infos['of_size'] = utils.get_text_volume(arvl_str_infos['text'], config.SCD4_FONT_12) - (matrix_manager.MATRIX_SIZE[0] - x_loca_bus_arvl[1])
    if arvl_str_infos['of_size'] > 0:
        arvl_str_infos['overflow'] = True
    
    # create display
    display = Image.new('RGB', matrix_manager.MATRIX_SIZE, "black")
    draw = ImageDraw.Draw(display)
    draw.fontmode = "1"
    
    station_title_align = utils.get_text_align_space(matrix_manager.MATRIX_SIZE[0], station_title, config.SCD4_FONT_12)
    station_title_info = {
        'text': station_title,
        'x_loca': station_title_align,
        'overflow': False,
        'frame_cnt': 0,
        'mv_cnt': 0
    }
    if utils.get_text_volume(station_title, config.SCD4_FONT_12) > matrix_manager.MATRIX_SIZE[0]:
        station_title_info['overflow'] = True
        station_title_info['x_loca'] = 0
        station_title_info['of_size'] = utils.get_text_volume(station_title, config.SCD4_FONT_12) - matrix_manager.MATRIX_SIZE[0]
    draw.text((station_title_info['x_loca'], y_loca[0]), station_title, "white", config.SCD4_FONT_12)
    
    for bus_data_list in utils.chunk_list(normal_infos):
        arvl_bus_end_mv_cnt = None
        station_title_end_mv_cnt = None
        
        arvl_bus_now_station_str_infos = [];
        bus_now_station_str_width = matrix_manager.MATRIX_SIZE[0] - x_loca[4]
        for index, bus_dict in enumerate(bus_data_list):
            # default value
            arvl_bus_now_station_str_info = {
                'text': bus_dict.get('nowStationName', ''),
                'overflow': False,
                'x_loca': x_loca[4]
            }
            
            # check overflow
            if bus_now_station_str_width < utils.get_text_volume(bus_dict.get('nowStationName', ''), config.SCD4_FONT_12):
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
                    draw.rectangle([(0, y_loca[0]), (matrix_manager.MATRIX_SIZE[0], y_loca[1]-1)], fill="black")
                    draw.text((station_title_info['x_loca'], y_loca[0]), station_title_info['text'], "white", config.SCD4_FONT_12)
                    
            draw.rectangle([(0, y_loca[1]), (matrix_manager.MATRIX_SIZE[0], y_loca[4]-1)], fill="black")
            for index, bus_dict in enumerate(bus_data_list):
                if frame >= 40 and arvl_bus_now_station_str_infos[index]['overflow']:
                    arvl_bus_now_station_str_infos[index]['x_loca'] -= 1
                
                bus_routeTypeCd = bus_dict.get("routeTypeCd", "-1")
                
                # 5 print bus arvl station
                draw.text((arvl_bus_now_station_str_infos[index]['x_loca'], y_loca[index+1]), arvl_bus_now_station_str_infos[index]['text'], "white", config.SCD4_FONT_12)
                draw.rectangle((x_loca[0], y_loca[index+1], x_loca[4]-1, y_loca[index+2]-1), fill="black")
                
                # 1 print bus icon
                draw.bitmap((x_loca[0], y_loca[index+1]), config.BUS_ICON, bus_type_color.get(bus_routeTypeCd, "white"));
                
                # 2 print route name
                draw.text((x_loca[1], y_loca[index+1]), bus_dict.get('routeName', ''), "white", config.SCD4_FONT_12)
                
                # 3 print remain seat grade
                remain_seat_str_align_val = utils.get_text_align_space(x_loca[3]-x_loca[2], bus_dict.get('remainSeatGrade'), config.SCD4_FONT_12)
                draw.text((x_loca[2]+remain_seat_str_align_val, y_loca[index+1]), bus_dict.get('remainSeatGrade'), bus_dict.get('remainSeatGradeColor'), config.SCD4_FONT_12)
                
                # 4 print predict time
                predict_time_str_align_val = utils.get_text_align_space(x_loca[4]-x_loca[3], f"{bus_dict.get('predictTime1', '')}분", config.SCD4_FONT_12)
                draw.text((x_loca[3]+predict_time_str_align_val, y_loca[index+1]), f"{bus_dict.get('predictTime1', '')}분", "aqua", config.SCD4_FONT_12)
            
            # 2 print arvl bus str
            draw.rectangle(((x_loca_bus_arvl[1], y_loca[4]), (matrix_manager.MATRIX_SIZE[0], matrix_manager.MATRIX_SIZE[1])), fill="black")
            draw.text((arvl_str_infos['x_loca'], y_loca[4]), arvl_str_infos['text'], "white", config.SCD4_FONT_12)
            
            # 1 print arvl bus title
            draw.rectangle(((0, y_loca[4]), (x_loca_bus_arvl[1]-1, matrix_manager.MATRIX_SIZE[1])), fill="black")
            draw.text((x_loca_bus_arvl[0], y_loca[4]), "곧도착:", "white", config.SCD4_FONT_12)
            
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
            
            matrix_manager.refresh(display)
            time.sleep(0.02)