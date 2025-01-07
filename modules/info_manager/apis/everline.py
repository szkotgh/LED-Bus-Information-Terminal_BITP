'''# Everline API Module
용인 에버라인 실시간 열차 정보 API 모듈.<br>
Github: https://github.com/suzukaotto/everline_api.git
'''

import requests
import datetime
import time
import threading

# Station Name List
STATION_NAME = [
    ['기흥', 'Giheung'],
    ['강남대', 'KANGNAM UNIV.'],
    ['지석', 'JISEOK'],
    ['어정', 'EOJEONG'],
    ['동백', 'DONGBAEK'],
    ['초당', 'CHODANG'],
    ['삼가', 'SAMGA'],
    ['시청·용인대', 'Cityhall·Yongin Univ'],
    ['명지대', 'MYONGJI UNIV.'],
    ['김량장', 'GIMYANGJANG'],
    ['용인중앙시장', 'Yongin Jungang Market'],
    ['고진', 'GOJIN'],
    ['보평', 'BOPYEONG'],
    ['둔전', 'DUNJEON'],
    ['전대·에버랜드', 'JEONDAE·EVERLAND']
]

# Station Code List
STATION_CODE = {
    "Y110": "기흥",
    "Y111": "강남대",
    "Y112": "지석",
    "Y113": "어정",
    "Y114": "동백",
    "Y115": "초당",
    "Y116": "삼가",
    "Y117": "시청·용인대",
    "Y118": "명지대",
    "Y119": "김량장",
    "Y120": "용인중앙시장",
    "Y121": "고진",
    "Y122": "보평",
    "Y123": "둔전",
    "Y124": "전대·에버랜드"
}
STATION_CODE_UPWARD   = ["Y124", "Y123", "Y122", "Y121", "Y120", "Y119", "Y118", "Y117", "Y116", "Y115", "Y114", "Y113", "Y112", "Y111", "Y110"] # 상행선 역 코드
STATION_CODE_DOWNWARD = ["Y110", "Y111", "Y112", "Y113", "Y114", "Y115", "Y116", "Y117", "Y118", "Y119", "Y120", "Y121", "Y122", "Y123", "Y124"] # 하행선 역 코드

# Station Duration Time
STATION_DURATION_UP = [ 96, 82, 77, 86, 122, 172, 79, 75, 62, 70, 76, 124, 85, 100 ];    # 상행선 각 역 사이의 소요 시간
STATION_DURATION_DOWN = [ 89, 74, 78, 83, 121, 147, 79, 77, 64, 71, 102, 110, 77, 100 ]; # 하행선 각 역 사이의 소요 시간

# updownCode 
TRAIN_UPWARD   = "1" # 상행
TRAIN_DOWNWARD = "2" # 하행

# Status Code
TRAIN_RETURN = "1" # 열차 회송
TRAIN_STOP   = "2" # 열차 정차
TRAIN_START  = "3" # 열차 출발

# Train Intervals
TRAIN_INTERVALS = {
    "Weekday": [
        {"start": 0,    "end": 459,  "interval": None},
        {"start": 530,  "end": 659,  "interval": 10},
        {"start": 700,  "end": 859,  "interval": 3},
        {"start": 900,  "end": 1659, "interval": 6},
        {"start": 1700, "end": 1959, "interval": 4},
        {"start": 2000, "end": 2059, "interval": 6},
        {"start": 2100, "end": 2159, "interval": 6},
        {"start": 2200, "end": 2359, "interval": 10},
    ],
    "Weekend": [
        {"start": 0,    "end": 459,  "interval": None},
        {"start": 530,  "end": 659,  "interval": 10},
        {"start": 700,  "end": 2059, "interval": 6},
        {"start": 2100, "end": 2359, "interval": 10},
    ],
}
def get_train_interval(_current_time, _is_weekend=False):
    """
    current_time: 현재 시간 (HHMM 형식, 예: 1543)
    is_weekend: 주말 여부 (True면 주말/공휴일, False면 평일)
    """
    schedule = TRAIN_INTERVALS["Weekend"] if _is_weekend else TRAIN_INTERVALS["Weekday"]
    
    _current_time = int(_current_time)
    current_minutes = (_current_time // 100) * 60 + (_current_time % 100)
    
    for time_range in schedule:
        start_minutes = (time_range["start"] // 100) * 60 + (time_range["start"] % 100)
        end_minutes = (time_range["end"] // 100) * 60 + (time_range["end"] % 100) + 1
        
        if start_minutes <= current_minutes < end_minutes:
            return time_range["interval"]
    
    return None

def cal_percent(_part, _whole, _round=2, _max=100):
    if _whole == 0:
        return 0
    cal_val = round(((_part / _whole) * 100), _round)
    if cal_val > _max:
        return _max
    return cal_val

class EverlineAPI:
    '''# Everline API Class
    ## Methods'''
    def __init__(self, req_url="https://everlinecu.com/api/api009.json"):
        self.req_url = req_url
        self.data = None
        self.last_update = None
        self.auto_update_thread = None
        self.auto_update_enabled = True

    def get_data(self, _time_out=3):
        try:
            response = requests.get(self.req_url, timeout=_time_out)
            response.raise_for_status()
            if response.status_code == 200:
                self.data = response.json()
                self.last_update = datetime.datetime.now()
                return True
            return False
        except:
            return False

    def start_auto_update(self, _interval=1):
        """Start auto update thread"""
        if self.auto_update_thread is not None:
            return False

        def update():
            while True:
                if not self.auto_update_enabled:
                    self.auto_update_thread = None
                    break
                
                # Update data. If failed, retry.
                try:
                    self.get_data()
                except:
                    continue
                
                time.sleep(_interval)

        self.auto_update_enabled = True
        self.auto_update_thread = threading.Thread(target=update, daemon=True)
        self.auto_update_thread.start()
        return True

    def stop_auto_update(self):
        if self.auto_update_thread is None:
            return False
        self.auto_update_enabled = None
        return True
    
    def get_train_count(self) -> int:
        if self.data == None:
            return None
        
        train_count = self.data.get("data", None)
        if train_count == None:
            return None
        return len(train_count)
    
    def get_train_info(self) -> list:
        if self.data == None:
            return None
        
        train_infos = self.data.get("data", None)
        if train_infos == None:
            return None

        # Add driving completion rate, (0~100%)
        for index, train_info in enumerate(train_infos):
            ## Train Info Parsing
            train_updown = train_info["updownCode"]
            train_time = int(train_info["time"])
            train_status = train_info["StatusCode"]
            train_stcode = train_info["StCode"]
            train_destcode = train_info["DestCode"]
            if train_updown == TRAIN_UPWARD:
                train_now_stindex = STATION_CODE_UPWARD.index(train_stcode)
                train_duration = STATION_DURATION_UP[train_now_stindex] if train_stcode != train_destcode else 0
            else:
                train_now_stindex = STATION_CODE_DOWNWARD.index(train_stcode)
                train_duration = STATION_DURATION_DOWN[train_now_stindex] if train_stcode != train_destcode else 0
            
            ## Train driving completion rate
            train_rate = cal_percent(train_time, train_duration)
            
            ## Info insert
            train_infos[index]["driveRate"] = train_rate

        return train_infos