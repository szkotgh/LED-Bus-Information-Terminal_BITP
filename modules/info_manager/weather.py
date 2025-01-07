import json
import os
import sys
import datetime
import requests
import xmltodict
import modules.utils as utils
import modules.config as config

code_info = {
    'WTS': '날씨정보', # 별도 추가 항목
    'POP': '강수확률', 'PTY': '강수형태', 'PCP': '1시간 강수량', 'REH': '습도',
    'SNO': '1시간 신적설', 'SKY': '하늘상태', 'TMP': '1시간 기온', 'TMN': '일 최저기온',
    'TMX': '일 최고기온', 'UUU': '풍속(동서성분)', 'VVV': '풍속(남북성분)', 'WAV': '파고',
    'VEC': '풍향', 'WSD': '풍속'
}

# 코드 단위 (단기예보)
code_unit = {
    'WTS': None, # 별도 추가 항목
    'POP': '%', 'PTY': '[코드값]', 'PCP': '[범주 (1mm)]', 'REH': '%', 'SNO': '[범주 (1cm)]',
    'SKY': '[코드값]', 'TMP': '℃', 'TMN': '℃', 'TMX': '℃', 'UUU': 'm/s',
    'VVV': 'm/s', 'WAV': 'M', 'VEC': 'deg', 'WSD': 'm/s'
}

SKY_info = {
    '-1': '정보없음', # 별도 추가 항목
    '1': '맑음', '3': '구름많음', '4': '흐림'
}

PTY_info = {
    '-1': '정보없음', # 별도 추가 항목
    '0': '없음', '1': '비', '2': '비/눈', '3': '눈',
    '4': '소나기', '5': '빗방울', '6': '빗방울눈날림', '7': '눈날림'
}

FineDust_Grade = {
    '-1': '정보없음',
    '1': '좋음', '2': '보통', '3': '나쁨', '4': '매우나쁨'
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

def get_vilage_fcst(nx, ny, base_date, base_time, num_of_rows='1000', page_no='1', data_type='XML'):
    f_response = create_default_response()

    req_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
    req_params = {
        'serviceKey': str(config.utils.get_env_key('SERVICE_KEY')),
        'numOfRows': str(num_of_rows),
        'pageNo': str(page_no),
        'dataType': str(data_type),
        'base_date': str(base_date),
        'base_time': str(base_time),
        'nx': str(ny),  # ? bus api 부분에서 nx, ny를 거꾸로 줌...
        'ny': str(nx)
    }

    res_content = make_request(req_url, req_params)
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
            'result': res_content['response']['body']['items']['item']
        })

    return f_response

def get_fine_dust_info(returnType="xml", sidoName="경기", ver="1.0"):
    f_response = create_default_response()

    req_url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    req_params = {
        "serviceKey": config.utils.get_env_key('SERVICE_KEY'),
        "returnType": returnType,
        "numOfRows": 1000,
        "pageNo": 1,
        "sidoName": sidoName,
        "ver": ver,
    }

    res_content = make_request(req_url, req_params)
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
            'result': res_content['response']['body']['items']['item']
        })

    return f_response