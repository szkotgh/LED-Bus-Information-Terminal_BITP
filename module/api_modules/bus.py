r"""
BUS.PY
------
버스 정보와 관련된 객체와 변수가 있는 모듈입니다.
버스 정보를 얻는 API를 손쉽게 호출할 수 있습니다.

#### 버스 정보 API 사용하기
모듈의 bus_api_requester 객체를 참조하십시오.

#### 버스 관련 정보 변수
| 변수명             |   | 비고                          |
| ------------------ | - | ----------------------------- |
| route_type_color   |   | 노선 유형별 색상 모음 (dict)  |
| route_type_code    |   | 노선 유형 코드 모음 (dict)    |
| drive_region_id    |   | 운행지역 아이디 모음 (dict)   |
| normal_statu_code  |   | 기본 API 에러코드 모음 (dict) |
| openapi_statu_code |   | Open API 에러코드 오름 (dict) |
"""

import sys
import datetime

# Import requests
try:
    import requests
except Exception as e:
    sys.exit(f'requests module import failed : {e}')
# Import xmltodict
try:
    import xmltodict
except Exception as e:
    sys.exit(f'xmltodict module import failed : {e}')
# Import module.utils
try:
    import module.utils as utils
except Exception as e:
    sys.exit(f'module.utils module import failed : {e}')

# 노선 유형 코드
route_type_code = {
    '11' :  '직행좌석형시내버스',
    '12' :  '좌석형시내버스',
    '13' :  '일반형시내버스',
    '14' :  '광역급행형시내버스',
    '15' :  '따복형 시내버스',
    '16' :  '경기순환버스',
    '21' :  '직행좌석형농어촌버스',
    '22' :  '좌석형농어촌버스',
    '23' :  '일반형농어촌버스',
    '30' :  '마을버스',
    '41' :  '고속형시외버스',
    '42' :  '좌석형시외버스',
    '43' :  '일반형시외버스',
    '51' :  '리무진공항버스',
    '52' :  '좌석형공항버스',
    '53' :  '일반형공항버스',
}
# 노선 유형 별 색상
route_type_color = {
    "11" : "red",
    "13" : "lime",
    "14" : "red",
    "30" : "yellow",
    "43" : "darkviolet",
    "51" : "sienna"
}

# 운행지역 아이디
drive_region_id = {
    '01' : '가평군',
    '02' : '고양시',
    '03' : '과천시',
    '04' : '광명시',
    '05' : '광주시',
    '06' : '구리시',
    '07' : '군포시',
    '08' : '김포시',
    '09' : '남양주시',
    '10' : '동두천시',
    '11' : '부천시',
    '12' : '성남시',
    '13' : '수원시',
    '14' : '시흥시',
    '15' : '안산시',
    '16' : '안성시',
    '17' : '안양시',
    '18' : '양주시',
    '19' : '양평군',
    '20' : '여주군',
    '21' : '연천군',
    '22' : '오산시',
    '23' : '용인시',
    '24' : '의왕시',
    '25' : '의정부시',
    '26' : '이천시',
    '27' : '파주시',
    '28' : '평택시',
    '29' : '포천시',
    '30' : '하남시',
    '31' : '화성시',
    '32' : '서울특별시',
    '33' : '인천광역시',
}

# bus api class
class bus_api_requester:
    r"""
BUS API REQUESTER
-----------------
버스 정보 관련 API를 요청하고 관리하는 객체
- 경기도 정류소 조회
- 경기도 버스도착정보 조회
- 경기도 버스노선 조회/노선정보항목조회
- 경기도 버스노선 조회/경유정류소목록조회

### 필요인자
| 항목명      |   | 항목설명                 |
| ----------- | - | ------------------------ |
| SERVICE_KEY |   | API 요청에 필요한 인증키 |

등록한 SERVICE_KEY는 API 요청 시 사용됩니다.
    """
    def __init__(self, SERVICE_KEY):
        self.SERVICE_KEY = str(SERVICE_KEY)
        self.api_timeout = 5
    
    def get_station_info(self, keyword:str) -> dict:
        r"""
경기도 정류소 조회
------------------
정류소명/번호에 해당하는 정류소 목록(정류소명, ID, 정류소번호, 좌표값, 중앙차로여부 등)을 제공한다.

### 요청인자
| 항목명  |   | 항목설명                       |
| ------- | - | ------------------------------ |
| keyword |   | 정류소명 또는 번호(2자리 이상) |

### 응답 메세지 명세
| 항목명      |   | 항목설명                                  |
| ----------- | - | ----------------------------------------- |
| stationId   |   | 정류소ID                                  |
| stationName |   | 정류소 명칭                               |
| mobileNo    |   | 정류소 고유모바일번호                     |
| regionName  |   | 정류소 위치 지역명                        |
| districtCd  |   | 노선 관할지역코드(1:서울, 2:경기, 3:인천) |
| centerYn    |   | 중앙차로 여부 (N:일반, Y:중앙차로)        |
| x           |   | 정류소 X 좌표 (WGS84)                     |
| y           |   | 정류소 Y 좌표 (WGS84)                     |

### 비고
데이터 중복 시 가장 첫 번쨰 데이터 반환.
API 결과는 'result'하위에 저장. 요청 실패 시 'result' None로 반환
        """
        # default response
        f_response = {
            'queryTime'  : utils.get_now_ftime(),
            'apiSuccess' : False,
            'apiParam'   : f"keyword={keyword}",
            'rstCode'    : -1,
            'rstMsg'     : utils.get_rst_msg(-1),
            'result'     : None
        }
        
        # request
        request_url = 'http://apis.data.go.kr/6410000/busstationservice/getBusStationList'
        params = {
            'serviceKey' : str(self.SERVICE_KEY),
            'keyword'    : str(keyword)
        }
        
        try:
            response = requests.get(url=request_url, params=params, timeout=self.api_timeout)
            response.raise_for_status()
        except:
            return f_response
        
        response = xmltodict.parse(response.content)
        
        detect_rst = utils.detect_response_error(response)
        rstCode = detect_rst['rstCode']
        rstMsg = detect_rst['rstMsg']
        
        f_response = {}
        if rstCode in ['0', '00']:
            f_response.update({
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : True,
                'apiParam'   : f"keyword={keyword}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : response['response']['msgBody']['busStationList'] if type(response['response']['msgBody']['busStationList']) == dict else response['response']['msgBody']['busStationList'][0]
            })
        else:
            f_response.update({
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : False,
                'apiParam'   : f"keyword={keyword}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : None
            })
        
        return f_response
        
    def get_bus_arrival(self, stationId:str) -> dict:
        r"""
경기도 버스도착정보 조회
------------------
해당 정류소에 정차하는 모든 노선에 대한 첫번째/두번째 도착예정 버스의 위치정보와 도착예정시간, 빈자리, 저상버스 정보를 제공하는 버스도착정보목록서비스

### 요청인자
| 항목명    |   | 항목설명  |
| --------- | - | --------- |
| stationId |   | 정류소 ID |

### 응답 메세지 명세
| 항목명         |   | 항목설명                                                               |
| -------------- | - | ---------------------------------------------------------------------- |
| stationId      |   | 정류소 ID                                                              |
| routeId        |   | 노선 ID                                                                |
| locationNo1    |   | 현재 버스위치 (몇 번쨰 전 정류소)                                      |
| predictTime1   |   | 버스도착예정시간 (몇 분후 도착 예정)                                   |
| lowPlate1      |   | 저상버스여부 (0: 일반버스, 1: 저상버스)                                |
| plateNo1       |   | 차량번호 (번호판 번호)                                                 |
| remainSeatCnt1 |   | 빈자리수 (-1: 정보없음, 0-:빈자리 수)                                  |
| locationNo2    |   | 현재 버스위치 (몇 번쨰 전 정류소)                                      |
| predictTime2   |   | 버스도착예정시간 (몇 분후 도착 예정)                                   |
| lowPlate2      |   | 저상버스여부 (0: 일반버스, 1: 저상버스)                                |
| plateNo2       |   | 차량번호 (번호판 번호)                                                 |
| remainSeatCnt2 |   | 빈자리수 (-1: 정보없음, 0-:빈자리 수)                                  |
| staOrder       |   | 노선의 정류소순번                                                      |
| flag           |   | 상태구분 (RUN: 운행중, PASS: 운행중, STOP: 운행종료, WAIT: 회차지대기) |

### 비고
모종의 오류로 get 실패 시 None형 반환
        """
        # default response
        f_response = {
            'queryTime'  : utils.get_now_ftime(),
            'apiSuccess' : False,
            'apiParams'  : f"stationId={stationId}",
            'rstCode'    : -1,
            'rstMsg'     : utils.get_rst_msg(-1),
            'result'     : None
        }
        
        request_url = 'http://apis.data.go.kr/6410000/busarrivalservice/getBusArrivalList'
        params = {
            'serviceKey' : str(self.SERVICE_KEY),
            'stationId'  : str(stationId)
        }
        
        try:
            response = requests.get(url=request_url, params=params, timeout=self.api_timeout)
            response.raise_for_status()
        except Exception as ERROR:
            print(f"API Request fail: {ERROR}")
            return None
        
        response = xmltodict.parse(response.content)
        
        detect_rst = utils.detect_response_error(response)
        rstCode = detect_rst['rstCode']
        rstMsg = detect_rst['rstMsg']
        
        f_response = {}
        if rstCode in ['0', '00']:
            f_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : True,
                'apiParams'  : f"stationId={stationId}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : [response['response']['msgBody']['busArrivalList']] if type(response['response']['msgBody']['busArrivalList']) == dict else response['response']['msgBody']['busArrivalList']
            }
        else:
            f_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : False,
                'apiParams'  : f"stationId={stationId}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : None
            }
            # return None
        
        return f_response
    
    def get_bus_info(self, routeId:str) -> dict:
        r"""
경기도 버스노선 조회/노선정보항목조회
------------------
노선ID에 해당하는 노선의 기본 정보 및 배차 정보를 조회한다.

### 요청인자
| 항목명  |   | 항목설명 |
| ------- | - | -------- |
| routeId |   | 노선 ID  |

### 응답 메세지 명세
| 항목명           |   | 항목설명                                 |
| ---------------- | - | ---------------------------------------- |
| routeId          |   | 노선 ID                                  |
| routeName        |   | 노선번호                                 |
| routeTypeCd      |   | 노선유형코드 (route_type_code 변수 참조) |
| routeTypeName    |   | 노선유형명                               |
| startStationId   |   | 기점정류소 ID                            |
| startStationName |   | 기점정류소 명칭                          |
| startMobileNo    |   | 기점정류소 고유모바일번호                |
| endStationId     |   | 종점정류소 ID                            |
| endStationName   |   | 종점정류소명칭                           |
| endStationNo     |   | 종점정류소 고유모바일번호                |
| regionName       |   | 노선 운행지역                            |
| districtCd       |   | 노선 관할지역코드                        |
| upFirstTime      |   | 평일 기점 첫차 출발시간                  |
| upLastTime       |   | 평일 기점 막차 출발시간                  |
| downFirstTIme    |   | 평일 종점 첫차 출발시간                  |
| downLastTime     |   | 평일 종점 막차 출발시간                  |
| peekAlloc        |   | 평일 최소 배차시간(분)                   |
| nPeekAlloc       |   | 평일 최대 배차시간(분)                   |
| companyId        |   | 노선 운행 운수업체 ID                    |
| companyName      |   | 노선 운행 운수업체 명칭                  |
| companyTEl       |   | 노선 운행 운수업체 전화번호              |

### 비고
모종의 오류로 get 실패 시 None형 반환
        """
        request_url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteInfoItem'
        params = {
            'serviceKey' : str(self.SERVICE_KEY),
            'routeId'    : str(routeId)
        }
        try:
            response = requests.get(url=request_url, params=params, timeout=self.api_timeout)
            response.raise_for_status()
        except Exception as ERROR:
            print(f"API Request fail: {ERROR}")
            err_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : False,
                'apiParams'  : f"routeId={routeId}",
                'rstCode'    : -1,
                'rstMsg'     : f"API 요청에 실패했습니다. {ERROR}",
                'result'     : None
            }
            return err_response
        
        response = xmltodict.parse(response.content)
        
        detect_rst = utils.detect_response_error(response)
        rstCode = detect_rst['rstCode']
        rstMsg = detect_rst['rstMsg']
        
        f_response = {}
        if rstCode in ['0', '00']:
            f_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : True,
                'apiParams'  : f"routeId={routeId}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : response['response']['msgBody']['busRouteInfoItem']
            }
        else:
            f_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : False,
                'apiParams'  : f"routeId={routeId}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : None
            }
            # return None
        
        return f_response
    
    def get_bus_transit_route(self, routeId:str) -> dict:
        r"""
경기도 버스노선 조회/경유정류소목록조회
------------------
노선 ID에 해당하는 노선의 경유정류소 목록을 조회한다.

### 요청인자
| 항목명  |   | 항목설명 |
| ------- | - | -------- |
| routeId |   | 노선 ID  |

### 응답 메세지 명세
| 항목명      |   | 항목설명                                      |
| ----------- | - | --------------------------------------------- |
| stationId   |   | 정류소 ID                                     |
| stationSeq  |   | 노선의 정류소 순번                            |
| stationName |   | 정류소 명칭                                   |
| mobileNo    |   | 정류소 고유모바일번호                         |
| regionName  |   | 정류소 위치 지역명                            |
| districtCd  |   | 노선 관할지역코드 (1: 서울, 2: 경기, 3: 인천) |
| centerYn    |   | 중앙차로 여부 (N: 일반, Y: 중앙차로)          |
| turnYn      |   | 회차점 여부 (N: 일반, Y: 중앙차로)            |
| x           |   | 정류소 X 좌표 (WGS84)                         |
| y           |   | 정류소 Y 좌표 (WGS84)                         |

### 비고
모종의 오류로 get 실패 시 None형 반환
        """
        
        request_url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteStationList'
        params = {
            'serviceKey' : str(self.SERVICE_KEY),
            'routeId'    : str(routeId)
        }
        try:
            response = requests.get(url=request_url, params=params, timeout=self.api_timeout)
            response.raise_for_status()
        except Exception as ERROR:
            print(f"API Request fail: {ERROR}")
            err_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : False,
                'apiParams'  : f"routeId={routeId}",
                'rstCode'    : -1,
                'rstMsg'     : f"API 요청에 실패했습니다. {ERROR}",
                'result'     : None
            }
            return err_response
        
        response = xmltodict.parse(response.content)
        
        detect_rst = utils.detect_response_error(response)
        rstCode = detect_rst['rstCode']
        rstMsg = detect_rst['rstMsg']
        
        f_response = {}
        if rstCode in ['0', '00']:
            f_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : True,
                'apiParams'  : f"routeId={routeId}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : [response['response']['msgBody']['busRouteStationList']] if (response['response']['msgBody']['busRouteStationList']) == dict else response['response']['msgBody']['busRouteStationList']
            }
        else:
            f_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : False,
                'apiParams'  : f"routeId={routeId}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : None
            }
            # return None
        
        return f_response