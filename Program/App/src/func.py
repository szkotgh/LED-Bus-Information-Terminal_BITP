import requests, json, xmltodict, sys, os

def get_station_arvl_bus(serviceKey, stationId):
    url = 'http://apis.data.go.kr/6410000/busarrivalservice/getBusArrivalList'
    params = {
        'serviceKey' : serviceKey,
        'stationId'  : stationId
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    response = xml_to_dict(response.content)

    return response

def get_station_info(serviceKey, keyword):
    url = 'http://apis.data.go.kr/6410000/busstationservice/getBusStationList'
    params = {
        'serviceKey' : serviceKey,
        'keyword'    : keyword
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    response = xml_to_dict(response.content)

    return response

def api_data_error_check(response_data):
    errData = response_data.get('OpenAPI_ServiceResponse', None)
    
    if errData == None:
        return None
    
    errData = errData['cmmMsgHeader']
    
    errMsg           = errData['errMsg']
    returnAuthMsg    = errData['returnAuthMsg']
    returnReasonCode = errData['returnReasonCode']
    
    print(f"{errMsg}    {returnAuthMsg}    {returnReasonCode}")
    
    return returnReasonCode

def xml_to_dict(xml_data, indent=4) -> json:
    try:
        json_data = json.dumps(xmltodict.parse(xml_data), indent=indent)
        return json.loads(json_data)
    except Exception as e:
        print(e)
        return None

def cls():
    os.system('cls')

class ArvlBus:
    def __init__(self, flag, locationNo, lowPlate, plateNo, predictTime, remainSeatCnt, routeId, staOrder, stationId):
        self.flag          = flag
        self.locationNo    = locationNo
        self.lowPlate      = lowPlate
        self.plateNo       = plateNo
        self.predictTime   = predictTime
        self.remainSeatCnt = remainSeatCnt
        self.routeId       = routeId
        self.staOrder      = staOrder
        self.stationId     = stationId

class BusStation:
    def __init__(self, stationId, stationName, mobileNo, y, x):
        self.stationId   = stationId
        self.stationName = stationName
        self.mobileNo    = mobileNo
        self.gps_y       = y
        self.gps_x       = x
    