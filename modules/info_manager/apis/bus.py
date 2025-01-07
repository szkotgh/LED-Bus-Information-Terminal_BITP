import json
import sys
import datetime
import requests
import xmltodict
import modules.utils as utils
import modules.config as config

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

def make_request(url, params):
    try:
        response = requests.get(url=url, params=params, timeout=config.OPTIONS['api_timeout'])
        response.raise_for_status()
        return xmltodict.parse(response.content)
    except Exception as ERROR:
        return {'errorOcrd': True, 'errorMsg': str(ERROR)}

def process_response(res_content):
    detect_rst = utils.detect_response_error(res_content)
    resCode = detect_rst[0]
    resMsg = detect_rst[1]
    return resCode, resMsg

def create_default_response():
    return {
        'queryTime': utils.get_now_ftime(),
        'apiSuccess': False,
        'errorOcrd': False,
        'result': None
    }

def get_station_info(_keyword: str) -> dict:
    f_response = create_default_response()

    request_url = 'http://apis.data.go.kr/6410000/busstationservice/getBusStationList'
    params = {
        'serviceKey': str(utils.get_env_key('SERVICE_KEY')),
        'keyword': str(_keyword)
    }

    res_content = make_request(request_url, params)
    if 'errorOcrd' in res_content:
        f_response.update(res_content)
        return f_response

    resCode, resMsg = process_response(res_content)
    f_response.update({
        'resCode': resCode,
        'resMsg': resMsg
    })

    if resCode in ['0', '00']:
        f_response.update({
            'apiSuccess': True,
            'result': res_content['response']['msgBody']['busStationList'] if type(res_content['response']['msgBody']['busStationList']) == dict else res_content['response']['msgBody']['busStationList'][0]
        })

    return f_response

def get_bus_arrival(_stationId: str) -> dict:
    f_response = create_default_response()

    request_url = 'http://apis.data.go.kr/6410000/busarrivalservice/getBusArrivalList'
    params = {
        'serviceKey': str(utils.get_env_key('SERVICE_KEY')),
        'stationId': str(_stationId)
    }

    res_content = make_request(request_url, params)
    if 'errorOcrd' in res_content:
        f_response.update(res_content)
        return f_response

    resCode, resMsg = process_response(res_content)
    f_response.update({
        'resCode': resCode,
        'resMsg': resMsg
    })

    if resCode in ['0', '00']:
        f_response.update({
            'apiSuccess': True,
            'result': [res_content['response']['msgBody']['busArrivalList']] if type(res_content['response']['msgBody']['busArrivalList']) == dict else res_content['response']['msgBody']['busArrivalList']
        })

    return f_response

def get_bus_info(_routeId: str) -> dict:
    f_response = create_default_response()

    request_url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteInfoItem'
    params = {
        'serviceKey': str(utils.get_env_key('SERVICE_KEY')),
        'routeId': str(_routeId)
    }

    res_content = make_request(request_url, params)
    if 'errorOcrd' in res_content:
        f_response.update(res_content)
        return f_response

    resCode, resMsg = process_response(res_content)
    f_response.update({
        'resCode': resCode,
        'resMsg': resMsg
    })

    if resCode in ['0', '00']:
        f_response.update({
            'apiSuccess': True,
            'result': res_content['response']['msgBody']['busRouteInfoItem']
        })

    return f_response

def get_bus_transit_route(_routeId: str) -> dict:
    f_response = create_default_response()

    request_url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteStationList'
    params = {
        'serviceKey': str(utils.get_env_key('SERVICE_KEY')),
        'routeId': str(_routeId)
    }

    res_content = make_request(request_url, params)
    if 'errorOcrd' in res_content:
        f_response.update(res_content)
        return f_response

    resCode, resMsg = process_response(res_content)
    f_response.update({
        'resCode': resCode,
        'resMsg': resMsg
    })

    if resCode in ['0', '00']:
        f_response.update({
            'apiSuccess': True,
            'result': [res_content['response']['msgBody']['busRouteStationList']] if type(res_content['response']['msgBody']['busRouteStationList']) == dict else res_content['response']['msgBody']['busRouteStationList']
        })

    return f_response