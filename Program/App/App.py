import time, sys
from src.func import *

cls()

with open('Program\App\option.json', 'r') as f:
    option = json.load(f)

serviceKey = option.get('serviceKey', None)

if serviceKey == None:
    sys.exit("Service Key is not set")

bus_station_list = []
for busStation in option['busStationList']:    
    station_data = get_station_info(serviceKey, busStation['moblieNo'])
    
    if api_data_error_check(station_data) != None:
        continue
    
    station_data = station_data['response']['msgBody']['busStationList']

    # 역 중복 시 가장 첫 번째 역 선택
    if type(station_data) == list:
        station_data = station_data[0]
    
    stationId   = station_data.get('stationId', None)
    stationName = station_data.get('stationName', None)
    mobileNo    = station_data.get('mobileNo', None)
    y           = station_data.get('y', None)
    x           = station_data.get('x', None)
    
    bus_station_list.append(BusStation(stationId, stationName, mobileNo, y, x))

for bus_station in bus_station_list:
    bus_station.create_arvl_bus_list([])
    
    arvl_bus_data = get_station_arvl_bus(serviceKey, bus_station.stationId)
    
    api_data_error_check_return_value = api_data_error_check(arvl_bus_data)
    if api_data_error_check_return_value != None:
        # 도착 할 버스가 없는 경우 (4, 결과가 존재하지 않습니다)
        if api_data_error_check_return_value == 4:
            bus_station.arvl_bus_list.append(None)
        
    else:
        # 도착 할 버스가 있는 경우 객체 만들어 저장
        if arvl_bus_data['response']['msgBody']['busArrivalList'] == None:
            bus_station.arvl_bus_list.append(None)      
        
        elif type(arvl_bus_data['response']['msgBody']['busArrivalList']) == dict:
            arvl_bus_data = arvl_bus_data['response']['msgBody']['busArrivalList']

            flag          = arvl_bus_data.get('flag', None)
            locationNo    = int(arvl_bus_data.get('locationNo1', None))
            lowPlate      = arvl_bus_data.get('lowPlate1', None)
            plateNo       = arvl_bus_data.get('plateNo', None)
            predictTime   = arvl_bus_data.get('predictTime1', None)
            remainSeatCnt = arvl_bus_data.get('remainSeatCnt1', None)
            routeId       = arvl_bus_data.get('routeId', None)
            staOrder      = int(arvl_bus_data.get('staOrder', None))
            statioinId    = arvl_bus_data.get('stationId', None)
            
            bus_station.arvl_bus_list.append(ArvlBus(flag, locationNo, lowPlate, plateNo, predictTime, remainSeatCnt, routeId, staOrder, statioinId))
            
        elif type(arvl_bus_data['response']['msgBody']['busArrivalList']) == list:
            arvl_bus_data = arvl_bus_data['response']['msgBody']['busArrivalList']

            for arvl_bus in arvl_bus_data:
                flag          = arvl_bus.get('flag', None)
                locationNo    = int(arvl_bus.get('locationNo1', None))
                lowPlate      = arvl_bus.get('lowPlate1', None)
                plateNo       = arvl_bus.get('plateNo', None)
                predictTime   = arvl_bus.get('predictTime1', None)
                remainSeatCnt = arvl_bus.get('remainSeatCnt1', None)
                routeId       = arvl_bus.get('routeId', None)
                staOrder      = int(arvl_bus.get('staOrder', None))
                statioinId    = arvl_bus.get('stationId', None)
                
                bus_station.arvl_bus_list.append(ArvlBus(flag, locationNo, lowPlate, plateNo, predictTime, remainSeatCnt, routeId, staOrder, statioinId))
    
    for arvl_bus in bus_station.arvl_bus_list:
        # 도착할 버스가 없는 경우 건너뛰기
        if arvl_bus == None:
            break
        
        route_data = get_route_info(serviceKey, arvl_bus.routeId)
        if api_data_error_check(route_data) != None:
            continue
        
        route_order_data = get_route_order_info(serviceKey, arvl_bus.routeId)
        if api_data_error_check(route_order_data) != None:
            continue
        
        route_data = route_data['response']['msgBody']['busRouteInfoItem']
        
        routeName       = route_data.get('routeName', None)
        routeTypeCd     = route_data.get('routeTypeCd', None)
        routeNowStaName = route_order_data['response']['msgBody']['busRouteStationList'][arvl_bus.staOrder-1-arvl_bus.locationNo]['stationName']
        
        arvl_bus.add_route_info(routeName, routeTypeCd, routeNowStaName)

    if bus_station.arvl_bus_list[0] != None:
        bus_station.arvl_bus_list.sort(key=lambda x: x.locationNo)
    
    print(f"{bus_station.stationName}({bus_station.mobileNo})")
    
    for arvl_bus in bus_station.arvl_bus_list:
        # 도착할 버스가 없는 경우
        if arvl_bus == None:
            print("도착할 버스가 없습니다.")
            break
        
        print("{:6} ({:>2}분) ({:>2}번째 전) {:2}     {:10}".format(arvl_bus.routeName, arvl_bus.predictTime, arvl_bus.locationNo, arvl_bus.routeTypeCd, arvl_bus.routeNowStaName))
    
    print()