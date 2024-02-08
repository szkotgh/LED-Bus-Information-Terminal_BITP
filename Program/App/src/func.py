import requests, json, xmltodict, sys, os

def get_route_order_info(serviceKey, routeId):
    url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteStationList'
    params = {
        'serviceKey' : serviceKey,
        'routeId'  : routeId
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    response = xml_to_dict(response.content)

    return response
    

def get_route_info(serviceKey, routeId):
    url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteInfoItem'
    params = {
        'serviceKey' : serviceKey,
        'routeId'  : routeId
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    response = xml_to_dict(response.content)

    return response

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

def api_data_error_check(response_data) -> None or int:
    errData = response_data.get('OpenAPI_ServiceResponse', None)
    
    if errData == None:
        # 일반 response 시
        errData = response_data['response']['msgHeader']
        
        resultCode = int(errData['resultCode'])
        resultMsg  = get_api_result_code_message(resultCode)
        
        if resultCode == 0:
            return None
        
        elif resultCode == 4:
            return resultCode
        
        else:
            print(f"{resultMsg}    {resultCode}")
            return resultCode

    else:
        # OpenAPI_ServiceResponse 발생 시
        errData = errData['cmmMsgHeader']
        
        errMsg           = errData['errMsg']
        returnAuthMsg    = errData['returnAuthMsg']
        returnReasonCode = int(errData['returnReasonCode'])
        
        print(f"{errMsg}    {returnAuthMsg}    {returnReasonCode}")
        
        return returnReasonCode


def get_api_result_code_message(resultCode:int) -> str:
    resultMessages = {
        0:  "정상적으로 처리되었습니다.",
        1:  "시스템 에러가 발생하였습니다.",
        2:  "필수 요청 Parameter 가 존재하지 않습니다.",
        3:  "필수 요청 Parameter 가 잘못되었습니다.",
        4:  "결과가 존재하지 않습니다.",
        5:  "필수 요청 Parameter(인증키) 가 존재하지 않습니다.",
        6:  "등록되지 않은 키입니다.",
        7:  "사용할 수 없는(등록은 되었으나, 일시적으로 사용 중지된) 키입니다.",
        8:  "요청 제한을 초과하였습니다.",
        20: "잘못된 위치로 요청하였습니다. 위경도 좌표값이 정확한지 확인하십시오.",
        21: "노선번호는 1자리 이상 입력하세요.",
        22: "정류소명/번호는 1자리 이상 입력하세요.",
        23: "버스 도착 정보가 존재하지 않습니다.",
        31: "존재하지 않는 출발 정류소 아이디(ID)/번호입니다.",
        32: "존재하지 않는 도착 정류소 아이디(ID)/번호입니다.",
        99: "API 서비스 준비중입니다."
    }
    
    return resultMessages.get(resultCode, "알 수 없는 코드입니다.")


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

    def add_route_info(self, routeName, routeTypeCd, routeNowStaName):
        self.routeName       = routeName
        self.routeTypeCd     = routeTypeCd
        self.routeNowStaName = routeNowStaName
        
class BusStation:
    def __init__(self, stationId, stationName, mobileNo, y, x):
        self.stationId   = stationId
        self.stationName = stationName
        self.mobileNo    = mobileNo
        self.gps_y       = y
        self.gps_x       = x
    
    def create_arvl_bus_list(self, arvl_bus_list):
        self.arvl_bus_list = arvl_bus_list