from src.func import *

cls()

with open('Program\App\option.json', 'r') as f:
    option = json.load(f)

bus_station_list = []
for busStation in option['busStationList']:    
    station_data = get_station_info(option['serviceKey'], busStation['moblieNo'])
    
    if api_data_error_check(station_data) != None:
        continue
    
    stationId   = station_data['response']['msgBody']['busStationList']['stationId']
    stationName = station_data['response']['msgBody']['busStationList']['stationName']
    mobileNo    = station_data['response']['msgBody']['busStationList']['mobileNo']
    y           = station_data['response']['msgBody']['busStationList']['y']
    x           = station_data['response']['msgBody']['busStationList']['x']
    
    bus_station_list.append(BusStation(stationId, stationName, mobileNo, y, x))

arvl_bus_list = []
for bus_station in bus_station_list:
    print(f"{bus_station.stationName}({bus_station.mobileNo})")
    arvl_bus_data = get_station_arvl_bus(option['serviceKey'], bus_station.stationId)
    
    for arvl_bus in arvl_bus_data['response']['msgBody']['busArrivalList']:
        flag          = arvl_bus.get('flag', None)
        locationNo    = arvl_bus.get('locationNo1', None)
        lowPlate      = arvl_bus.get('lowPlate1', None)
        plateNo       = arvl_bus.get('plateNo', None)
        predictTime   = arvl_bus.get('predictTime1', None)
        remainSeatCnt = arvl_bus.get('remainSeatCnt1', None)
        routeId       = arvl_bus.get('routeId', None)
        staOrder      = arvl_bus.get('staOrder', None)
        statioinId    = arvl_bus.get('stationId', None)
        
        arvl_bus_list.append(ArvlBus(flag, locationNo, lowPlate, plateNo, predictTime, remainSeatCnt, routeId, staOrder, statioinId))
        
    for arvl_bus in arvl_bus_list:
        print(arvl_bus.routeId)
    
    print()
    
    
    
