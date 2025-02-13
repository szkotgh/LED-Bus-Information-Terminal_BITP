from datetime import timedelta
import json
import threading
import time
from modules import config
import modules.utils as utils

# 노선 유형 코드
route_type_code = {
    '11':  '직행좌석형시내버스', '12':  '좌석형시내버스', '13':  '일반형시내버스',
    '14':  '광역급행형시내버스', '15':  '따복형 시내버스', '16':  '경기순환버스',
    '21':  '직행좌석형농어촌버스', '22':  '좌석형농어촌버스', '23':  '일반형농어촌버스',
    '30':  '마을버스', '41':  '고속형시외버스', '42':  '좌석형시외버스',
    '43':  '일반형시외버스', '51':  '리무진공항버스', '52':  '좌석형공항버스',
    '53':  '일반형공항버스',
}
# 노선 유형 별 색상
route_type_color = {
    "11": "red", "13": "lime", "14": "red", "30": "yellow", "43": "darkviolet",
    "51": "sienna"
}
# 운행지역 아이디
drive_region_id = {
    '01': '가평군', '02': '고양시', '03': '과천시', '04': '광명시', '05': '광주시',
    '06': '구리시', '07': '군포시', '08': '김포시', '09': '남양주시', '10': '동두천시',
    '11': '부천시', '12': '성남시', '13': '수원시', '14': '시흥시', '15': '안산시',
    '16': '안성시', '17': '안양시', '18': '양주시', '19': '양평군', '20': '여주군',
    '21': '연천군', '22': '오산시', '23': '용인시', '24': '의왕시', '25': '의정부시',
    '26': '이천시', '27': '파주시', '28': '평택시', '29': '포천시', '30': '하남시',
    '31': '화성시', '32': '서울특별시', '33': '인천광역시',
}

class BusStationAPI:
    def __init__(self, _service_key, _init_station_data):
        self.service_key = _service_key
        
        self.init_station_data     = _init_station_data
        self.station_data          = utils.gen_response()
        self.arvl_bus_data         = utils.gen_response()
        self.station_finedust_data = utils.gen_response()
        self.station_weather_data  = utils.gen_response()
    
        self.is_station_data_inited = False
        self.last_arvl_bus_data_update_time = None
        
        self.auto_update_station_arvl_bus()
    
    def update_station_data(self):
        req_url = 'http://apis.data.go.kr/6410000/busstationservice/getBusStationList'
        req_params = {
            'serviceKey': self.service_key,
            'keyword': self.init_station_data['keyword']
        }
        
        result = utils.request_get_http(req_url, req_params, ['response', 'msgBody', 'busStationList'])
        self.station_data = result
        
        if self.station_data['apiSuccess'] == True:
            self.is_station_data_inited = True
    
    def get_arvl_bus_data(self):
        req_url = 'http://apis.data.go.kr/6410000/busarrivalservice/getBusArrivalList'
        req_params = {
            'serviceKey': self.service_key,
            'stationId': self.station_data['result']['stationId']
        }
        
        result = utils.request_get_http(req_url, req_params, ['response', 'msgBody', 'busArrivalList'])
        self.arvl_bus_data = result
        
        if self.arvl_bus_data['apiSuccess'] == True:
            self.last_arvl_bus_data_update_time = utils.get_now_datetime()
        
        if type(self.arvl_bus_data['result']) != list:
            self.arvl_bus_data['result'] = [] if self.arvl_bus_data['result'] == None else [self.arvl_bus_data['result']]
        
    
    def get_arvl_bus_info_data(self, _route_id):
        req_url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteInfoItem'
        req_params = {
            'serviceKey': self.service_key,
            'routeId': _route_id
        }
        
        result = utils.request_get_http(req_url, req_params, ['response', 'msgBody', 'busRouteInfoItem'])
        return result
    
    def get_arvl_bus_route_info_data(self, _route_id):
        url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteStationList'
        params = {
            'serviceKey': self.service_key,
            'routeId': _route_id
        }
        
        result = utils.request_get_http(url, params, ['response', 'msgBody', 'busRouteStationList'])
        return result
    
    def update_arvl_bus_data(self):
        self.get_arvl_bus_data()
        
        if self.arvl_bus_data['apiSuccess'] == False:
            return False
        
        arvl_bus_list = self.arvl_bus_data['result']
            
        for index, arvl_bus in enumerate(arvl_bus_list):
            route_id = arvl_bus['routeId']
            arvl_bus_info = self.get_arvl_bus_info_data(route_id)
            arvl_bus_route_info = self.get_arvl_bus_route_info_data(route_id)
            
            self.arvl_bus_data['result'][index].update({
                'busInfo': arvl_bus_info,
                'busRouteInfo': arvl_bus_route_info
            })
        
    def update_station_fine_dust_data(self, stationDong, sidoName, returnType="xml", ver="1.0"):
        req_url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
        req_params = {
            "serviceKey": self.service_key,
            "returnType": returnType,
            "numOfRows": 1000,
            "pageNo": 1,
            "sidoName": sidoName,
            "ver": ver,
        }

        result = utils.request_get_http(req_url, req_params, ['response', 'body', 'items', 'item'])
        self.station_finedust_data = result
        
        if self.station_finedust_data['apiSuccess'] == True:
            for result_item in self.station_finedust_data['result']:
                if result_item['stationName'] == stationDong:
                    self.station_finedust_data['result'] = result_item
                    break
    
    def update_station_weather_data(self, nx: int, ny: int, base_date, base_time, num_of_rows='1000', page_no='1', data_type='XML'):
        req_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
        req_params = {
            'serviceKey': self.service_key,
            'numOfRows': str(num_of_rows),
            'pageNo': str(page_no),
            'dataType': str(data_type),
            'base_date': str(base_date),
            'base_time': str(base_time),
            'nx': int(nx),
            'ny': int(ny)
        }

        result = utils.request_get_http(req_url, req_params, ['response', 'body', 'items', 'item'])
        self.station_weather_data = result
        
        return result
        
    def auto_update_station_arvl_bus(self):
        # update functions
        def update_station_arvl_bus():
            # station data init
            while self.is_station_data_inited == False:
                self.update_station_data()
                
                if self.is_station_data_inited:
                    break
                
                time.sleep(config.OPTIONS['bus']['arvlBusRefreshInterval'])
            
            with open(f'{self.init_station_data["keyword"]}_station_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.station_data, f, indent=4, ensure_ascii=False)
            
            # arvl bus auto data update
            while True:
                self.update_arvl_bus_data()
                with open(f'{self.init_station_data["keyword"]}_arvl_bus_data.json', 'w', encoding='utf-8') as f:
                    json.dump(self.arvl_bus_data, f, indent=4, ensure_ascii=False)
                time.sleep(config.OPTIONS['bus']['arvlBusRefreshInterval'])
        
        def update_station_finedust():
            while True:
                self.update_station_fine_dust_data('김량장동', "경기")
                with open(f'{self.init_station_data["keyword"]}_finedust_data.json', 'w', encoding='utf-8') as f:
                    json.dump(self.station_finedust_data, f, indent=4, ensure_ascii=False)
                time.sleep(config.OPTIONS['bus']['finedustInfoRefreshInterval'])
        
        def update_station_weather():
            base_time = ["0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300"]
            
            # wait for station data init
            while self.is_station_data_inited == False:
                if self.is_station_data_inited:
                    break
                time.sleep(1)
            
            # wait for finedust data init
            while True:
                station_x = int(float(self.station_data['result']['x']))
                station_y = int(float(self.station_data['result']['y']))
                
                today_datetime = utils.get_now_datetime()
                today_date = today_datetime.strftime("%Y%m%d")
                today_time = today_datetime.strftime("%H%M")
                
                sel_base_time = min(base_time, key=lambda t: abs(int(today_time) - int(t)))
                
                self.update_station_weather_data(station_y, station_x, today_date, sel_base_time)   # ? bus api 부분에서 nx, ny를 거꾸로 줌...
                with open(f'{self.init_station_data["keyword"]}_weather_data.json', 'w', encoding='utf-8') as f:
                    json.dump(self.station_weather_data, f, indent=4, ensure_ascii=False)
                
                if self.station_weather_data['apiSuccess'] == False:
                    time.sleep(1)
                    continue
                
                time.sleep(config.OPTIONS['bus']['weatherInfoRefreshInterval'])
        
        # Threads
        station_arvl_bus_update_thread = threading.Thread(target=update_station_arvl_bus)
        station_arvl_bus_update_thread.daemon = True
        station_arvl_bus_update_thread.start()
        
        station_weather_update_thread = threading.Thread(target=update_station_weather)
        station_weather_update_thread.daemon = True
        station_weather_update_thread.start()
        
        station_finedust_update_thread = threading.Thread(target=update_station_finedust)
        station_finedust_update_thread.daemon = True
        station_finedust_update_thread.start()
        