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
    'WTS' : '날씨정보', # 별도 추가 항목
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

# 코드 단위 (단기예보)
code_unit = {
    'WTS' : None, # 별도 추가 항목
    'POP' : '%',
    'PTY' : '[코드값]',
    'PCP' : '[범주 (1mm)]',
    'REH' : '%',
    'SNO' : '[범주 (1cm)]',
    'SKY' : '[코드값]',
    'TMP' : '℃',
    'TMN' : '℃',
    'TMX' : '℃',
    'UUU' : 'm/s',
    'VVV' : 'm/s',
    'WAV' : 'M',
    'VEC' : 'deg',
    'WSD' : 'm/s'
}

SKY_info = {
    '-1' : '정보없음', # 별도 추가 항목
    '1'  : '맑음',
    '3'  : '구름많음',
    '4'  : '흐림'
}

PTY_info = {
    None : '정보없음',
    '-1' : '정보없음', # 별도 추가 항목
    '0'  : '없음',
    '1'  : '비',
    '2'  : '비/눈',
    '3'  : '눈',
    '4'  : '소나기',
    '5'  : '빗방울',
    '6'  : '빗방울눈날림',
    '7'  : '눈날림'
}

FineDust_Grade = {
    '-1' : '정보없음',
    '1'  : '좋음',
    '2'  : '보통',
    '3'  : '나쁨',
    '4'  : '매우나쁨'
}

class weather_api_requester:
    def __init__(self, SERVICE_KEY, _OPTIONS):
        self.SERVICE_KEY = SERVICE_KEY
        self.OPTION = _OPTIONS
        self.api_timeout = self.OPTION['api_timeout']

    def get_vilage_fcst(self, nx, ny, base_date, base_time, num_of_rows='1000', page_no='1', data_type='XML'):
        # default response
        f_response = {
            'queryTime'  : utils.get_now_ftime(),
            'apiSuccess' : False,
            'reqParam'   : f"nx={nx},ny={ny},base_date={base_date},base_time={base_time},num_of_rows={num_of_rows},page_no={page_no},data_type={data_type}",
            'errorOcrd'  : False,
            'result'     : None
        }
        
        # request
        req_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
        req_params = {
            'serviceKey' : str(self.SERVICE_KEY),
            'numOfRows'  : str(num_of_rows),
            'pageNo'     : str(page_no),
            'dataType'   : str(data_type),
            'base_date'  : str(base_date),
            'base_time'  : str(base_time),
            'nx'         : str(ny),      # ? bus api 부분에서 nx, ny를 거꾸로 줌...
            'ny'         : str(nx)
        }
        
        try:
            response = requests.get(url=req_url, params=req_params, timeout=self.api_timeout)
            response.raise_for_status()
            res_content = xmltodict.parse(response.content)
        except Exception as ERROR:
            f_response['errorOcrd'] = True
            f_response['errorMsg']  = str(ERROR)
            return f_response
        
        # response process
        detect_rst = utils.detect_response_error(res_content)
        resCode = detect_rst[0]
        resMsg = detect_rst[1]
        f_response.update({
            'resCode' : resCode,
            'resMsg'  : resMsg
        })
        
        if resCode in ['0', '00']:
            f_response.update({
                'apiSuccess' : True,
                'result'     : res_content['response']['body']['items']['item']
            })
        
        return f_response
        
        detect_rst = utils.detect_response_error(res_content)
        rstCode = detect_rst['rstCode']
        rstMsg = detect_rst['rstMsg']
        
        if rstCode in ['0', '00']:
            f_response.update({
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : True,
                'apiParam'   : f"nx={nx},ny={ny},base_date={base_date},base_time={base_time},num_of_rows={num_of_rows},page_no={page_no},data_type={data_type}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : res_content['response']['body']['items']['item']
            })
        else:
            f_response.update({
                'queryTime'  : utils.get_now_ftime(),
                'apiSuccess' : False,
                'apiParam'   : f"nx={nx},ny={ny},base_date={base_date},base_time={base_time},num_of_rows={num_of_rows},page_no={page_no},data_type={data_type}",
                'rstCode'    : rstCode,
                'rstMsg'     : rstMsg,
                'result'     : None
            })
        
        return f_response
    
    def get_fine_dust_info(self, returnType="xml", sidoName="경기", ver="1.0"):
        # default response
        f_response = {
            'queryTime'  : utils.get_now_ftime(),
            'apiSuccess' : False,
            'reqParam'   : f"returnType={returnType},sidoName={sidoName},ver={ver}",
            'errorOcrd'  : False,
            'result'     : None
        }
        
        # request
        req_url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
        req_params = {
            "serviceKey" : self.SERVICE_KEY,
            "returnType" : returnType,
            "numOfRows"  : 1000,
            "pageNo"     : 1,
            "sidoName"   : sidoName,
            "ver"        : ver,
        }
        
        try:
            response = requests.get(url=req_url, params=req_params, timeout=self.api_timeout)
            response.raise_for_status()
            res_content = xmltodict.parse(response.content)
        except Exception as ERROR:
            f_response['errorOcrd'] = True
            f_response['errorMsg']  = str(ERROR)
            return f_response
        
        # response process
        detect_rst = utils.detect_response_error(res_content)
        resCode = detect_rst[0]
        resMsg = detect_rst[1]
        f_response.update({
            'resCode' : resCode,
            'resMsg'  : resMsg
        })
        if resCode in ['0', '00']:
            f_response.update({
                'apiSuccess' : True,
                'result'     : res_content['response']['body']['items']['item']
            })
        
        return f_response
        