'''
WEATHER.PY
----------
날씨와 관련된 객체와 변수가 있는 모듈입니다.
기온과 미세먼지를 얻는 API를 손쉽게 호출할 수 있습니다.
'''

import json
import os
import sys
import datetime

try:
    import requests
except Exception as e:
    sys.exit(f'requests module import failed : {e}')
try:
    import xmltodict
except:
    sys.exit(f'xmltodict module import failed : {e}')
try:
    import module.utils as utils
except:
    sys.exit(f'module.utils module import failed : {e}')

code_info = {
    'POP' : '강수확률',
    'PTY' : '강수형태',
    'PCP' : '1시간 강수량',
    'REH' : '습도',
    'SNO' : '1시간 신적설',
    'SKY' : '하늘상태',
    'TMP' : '1시간 기온',
    'TMN' : '일 최저기온',
    'TMX' : '일 최고기온',
    'UUU' : '풍속(동서성분)',
    'VVV' : '풍속(남북성분)',
    'WAV' : '파고',
    'VEC' : '풍향',
    'WSD' : '풍속'
}

SKY_info = {
    '1' : '맑음',
    '3' : '구름많음',
    '4' : '흐림'
}

PTY_info = {
    '0' : '없음',
    '1' : '비',
    '2' : '비/눈',
    '3' : '눈',
    '4' : '소나기',
    '5' : '빗방울',
    '6' : '빗방울눈날림',
    '7' : '눈날림'
}

class weather_api_requester:
    def __init__(self, SERVICE_KEY):
        self.SERVICE_KEY = SERVICE_KEY
        self.detect_response_error = utils.detect_response_error

    def get_vilage_fcst(self, nx, ny, base_date, base_time, num_of_rows='1000', page_no='1', data_type='XML'):
        url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
        params = {
            'serviceKey': self.SERVICE_KEY,
            'numOfRows': num_of_rows,
            'pageNo': page_no,
            'dataType': data_type,
            'base_date': base_date,
            'base_time': base_time,
            'nx': nx,
            'ny': ny
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except Exception as ERROR:
            print(f"API Request fail: {ERROR}")
            return None
        
        response = xmltodict.parse(response.text)
        
        detect_rst = self.detect_response_error(response)
        rstCode = detect_rst['rstCode']
        rstMsg = detect_rst['rstMsg']
        
        f_response = {}
        if rstCode in ['0', '00']:
            f_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : True,
                'apiParam'   : f"nx={nx},ny={ny},base_date={base_date},base_time={base_time},num_of_rows={num_of_rows},page_no={page_no},data_type={data_type}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : response['response']['body']['items']['item']
            }
        else:
            f_response = {
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : False,
                'apiParam'   : f"nx={nx},ny={ny},base_date={base_date},base_time={base_time},num_of_rows={num_of_rows},page_no={page_no},data_type={data_type}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : None
            }
            # return None
        
        return f_response