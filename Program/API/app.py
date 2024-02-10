import time, sys, os
import os.path as osp   


try:
    from dotenv import load_dotenv
except:
    sys.exit("dotenv module is not installed")

try:
    from API.func import *
except:
    sys.exit("func module not found")


# load option.json
try:
    with open(osp.join("Program", "API", "option.json"), 'r') as f:
        option = json.load(f)
except:
    sys.exit("option.json load failed")

# load serviceKey
try:
    load_dotenv(osp.join("Program", "API", ".env"))
    serviceKey = os.environ["SERVICE_KEY"]
except:
    sys.exit("serviceKey load failed")


def get_bus_station_list() -> list:
    # option.json 파일 내의 busStationList 순서대로 역 정보 가져와 객체 return
    bus_station_list = []
    for busStation in option.get('busStationList', None):
        ## 불러온 option 안에 busStationList이 없을 경우
        if busStation == None:
            raise Exception("The busStationList Key cannot be found in the option.json file.")
        
        ## busStationList 안에 moblieNo 불러오기
        station_moblieNo = busStation.get('moblieNo', None)
        ## busStationList 안에 moblieNo 이 없을 경우
        if station_moblieNo == None:
            raise Exception("The moblieNo Key cannot be found in the busStationList Key in the option.json file.")
        
        
        
        ## API Request
        station_data = get_station_info(serviceKey, busStation['moblieNo'])
        ## API Response data 결과 코드 확인
        api_data_error_check_value = api_data_error_check(station_data)
        if api_data_error_check_value == None:
            ### 값이 문제 없을 경우
            pass
        elif api_data_error_check_value == 4:
            ### 결과가 존재하지 않을 경우
            print(f"Station information does not exist. (Registered moblieNo: '{station_moblieNo}')")
            continue
        else:
            ### 기타 문제가 있을 경우
            print(f"A problem occurred and the stop object could not be created. (Registered moblieNo: '{station_moblieNo}')")
            continue
        
        
        
        ## 값 불러오기 및 객체 생성
        station_data = station_data['response']['msgBody']['busStationList']

        ### 역 정보 중복 시 가장 첫 번째 역 선택
        if type(station_data) == list:
            station_data = station_data[0]
        
        stationId = station_data.get('stationId', None)
        stationNm = station_data.get('stationName', None)
        mobileNo  = station_data.get('mobileNo', None)
        y         = station_data.get('y', None)
        x         = station_data.get('x', None)
        
        bus_station_list.append(BusStation(stationId, stationNm, mobileNo, y, x))
    
    return bus_station_list

def get_arvl_bus_list(bus_station:BusStation):
    # 버스도착정보 조회, 곧 도착 버스 별 정보 조회 및 추가
    
    
    
    ## API Request
    arvl_bus_data = get_station_arvl_bus(serviceKey, bus_station.stationId)
    api_data_error_check_value = api_data_error_check(arvl_bus_data) # API Response data 에러 확인
    if api_data_error_check_value == None:
        ## 값이 문제 없을 경우
        pass
    elif api_data_error_check_value == 4:
        ## 도착 할 버스가 없는 경우 (4, 결과가 존재하지 않습니다)
        bus_station.arvl_bus_list.append(None)
    else:
        ## 기타 문제가 있을 경우
        raise Exception(api_data_error_check_value)
    
    
        
    ## 도착 할 버스가 없는 경우 (busArrivalList None 형태일 경우)
    if arvl_bus_data['response']['msgBody']['busArrivalList'] == None:
        bus_station.arvl_bus_list.append(None)
    
    ## 도착 할 버스가 한 대일 경우
    elif type(arvl_bus_data['response']['msgBody']['busArrivalList']) == dict:
        arvl_bus_data = arvl_bus_data['response']['msgBody']['busArrivalList']
        
        flag          =     arvl_bus_data.get('flag', None)
        locationNo    = int(arvl_bus_data.get('locationNo1', None))
        lowPlate      =     arvl_bus_data.get('lowPlate1', None)
        plateNo       =     arvl_bus_data.get('plateNo', None)
        predictTime   = int(arvl_bus_data.get('predictTime1', None))
        remainSeatCnt =     arvl_bus_data.get('remainSeatCnt1', None)
        routeId       =     arvl_bus_data.get('routeId', None)
        staOrder      = int(arvl_bus_data.get('staOrder', None))
        statioinId    =     arvl_bus_data.get('stationId', None)
        
        bus_station.arvl_bus_list.append(ArvlBus(flag, locationNo, lowPlate, plateNo, predictTime, remainSeatCnt, routeId, staOrder, statioinId))
    
    # 도착할 버스가 여러 대인 경우
    elif type(arvl_bus_data['response']['msgBody']['busArrivalList']) == list:
        arvl_bus_data = arvl_bus_data['response']['msgBody']['busArrivalList']
        for arvl_bus in arvl_bus_data:
            flag          =     arvl_bus.get('flag', None)
            locationNo    = int(arvl_bus.get('locationNo1', None))
            lowPlate      =     arvl_bus.get('lowPlate1', None)
            plateNo       =     arvl_bus.get('plateNo', None)
            predictTime   = int(arvl_bus.get('predictTime1', None))
            remainSeatCnt =     arvl_bus.get('remainSeatCnt1', None)
            routeId       =     arvl_bus.get('routeId', None)
            staOrder      = int(arvl_bus.get('staOrder', None))
            statioinId    =     arvl_bus.get('stationId', None)
                        
            bus_station.arvl_bus_list.append(ArvlBus(flag, locationNo, lowPlate, plateNo, predictTime, remainSeatCnt, routeId, staOrder, statioinId))
    
    
    
    # 곧 도착 버스 별 부가정보 조회 및 추가, 곧 도착 여부 추가
    for arvl_bus in bus_station.arvl_bus_list:
        ## 부가정보 조회 및 추가
        ### 도착할 버스가 없는 경우 건너뛰기
        if arvl_bus == None:
            break
        
        route_data = get_route_info(serviceKey, arvl_bus.routeId)
        if api_data_error_check(route_data) != None:
            continue
        
        route_order_data = get_route_order_info(serviceKey, arvl_bus.routeId)
        if api_data_error_check(route_order_data) != None:
            continue
        
        route_data = route_data['response']['msgBody']['busRouteInfoItem']
        
        routeNm     = route_data.get('routeName', None)
        routeTypeCd   = route_data.get('routeTypeCd', None)
        routeNowStaNm = route_order_data['response']['msgBody']['busRouteStationList'][arvl_bus.staOrder-1-arvl_bus.locationNo]['stationName']
        
        ## 데이터 저장
        arvl_bus.routeNm       = routeNm
        arvl_bus.routeTypeCd   = routeTypeCd
        arvl_bus.routeNowStaNm = routeNowStaNm
        
        ## 곧 도착 여부 (3 정거장 이전인 경우)
        if arvl_bus.locationNo < 3:
            arvl_bus.is_arvl = True

    # 남은 도착 시간 순 정렬
    if bus_station.arvl_bus_list[0] != None:
        bus_station.arvl_bus_list.sort(key=lambda x: x.predictTime)
    
    return 0