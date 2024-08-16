import os
import sys
import logging
import json
import base64
from hashlib import md5
import dotenv
import datetime
import subprocess
try:
    import requests
except Exception as e:
    sys.exit(f"requests module import failed: {e}")

log_time_format = "%Z %x %X"
log_format = "%(asctime)s %(levelname)s [%(name)s] > %(message)s"
default_time_format = "%Y%m%d%H%M%S"

normalapi_error_code = {
    '-1' : '결과를 알 수 없습니다.',
    '0'  : '정상적으로 처리되었습니다.',
    '1'  : '시스템 에러가 발생하였습니다.',
    '2'  : '필수 요청 Parameter 가 존재하지 않습니다.',
    '3'  : '필수 요청 Parameter 가 잘못되었습니다.',
    '4'  : '결과가 존재하지 않습니다.',
    '5'  : '필수 요청 Parameter(인증키) 가 존재하지 않습니다.',
    '6'  : '등록되지 않은 키입니다.',
    '7'  : '사용할 수 없는(등록은 되었으나, 일시적으로 사용 중지된) 키입니다.',
    '8'  : '요청 제한을 초과하였습니다.',
    '20' : '잘못된 위치로 요청하였습니다. 위경도 좌표값이 정확한지 확인하십시오.',
    '21' : '노선번호는 1자리 이상 입력하세요.',
    '22' : '정류소명/번호는 1자리 이상 입력하세요.',
    '23' : '버스 도착 정보가 존재하지 않습니다.',
    '31' : '존재하지 않는 출발 정류소 아이디(ID)/번호입니다.',
    '32' : '존재하지 않는 도착 정류소 아이디(ID)/번호입니다.',
    '99' : 'API 서비스 준비중입니다.',
}

openapi_error_code = {
    '-1' : '결과를 알 수 없습니다.',
    '00' : '정상',
    '01' : '어플리케이션 에러',
    '02' : '데이터베이스 에러',
    '03' : '데이터없음 에러',
    '04' : 'HTTP 에러',
    '05' : '서비스 연결실패 에러',
    '10' : '잘못된 요청 파라메터 에러',
    '11' : '필수요청 파라메터가 없음',
    '12' : '해당 오픈API서비스가 없거나 폐기됨',
    '20' : '서비스 접근거부',
    '21' : '일시적으로 사용할 수 없는 서비스 키',
    '22' : '서비스 요청제한횟수 초과에러',
    '30' : '등록되지 않은 서비스키',
    '31' : '서비스키 사용 기간 만료',
    '32' : '서비스 제공 상태가 원활하지 않습니다',
    '33' : '서명되지 않은 호출',
    '34' : '보고서가 등록 되지 않음',
    '99' : '기타에러',
}



def get_now_ftime(time_format: str | None = default_time_format) -> str:
    time = datetime.datetime.now()
    f_time = time.strftime(time_format)
    return f_time

def convert_ftime(ftime_str: str, time_format: str | None = default_time_format) -> datetime.datetime:
    time = datetime.datetime.strptime(ftime_str, time_format)
    return time

def get_ip() -> str:
    try:
        ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip()
        ip_address = ip if ip else "address not found"
    except Exception:
        ip_address = "address not found"
    return ip_address

def get_rst_msg(rst_code, api_type: str = 'normal') -> str:
    '''
    api_type: 'normal' or 'openapi'
    '''
    rst_code = str(rst_code)
    if api_type == 'normal':
        return normalapi_error_code.get(rst_code, '결과를 알 수 없습니다.')
    elif api_type == 'openapi':
        return openapi_error_code.get(rst_code, '결과를 알 수 없습니다.')
    else:
        return '결과를 알 수 없습니다.'

def create_logger(logger_name, logger_file_path='log/mainlog.log', logger_set_level=logging.DEBUG, file_set_level=logging.DEBUG) -> logging.Logger:    
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_set_level)
    formatter = logging.Formatter(log_format, datefmt=log_time_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(logger_file_path, 'a', encoding='UTF-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_set_level)
    logger.addHandler(file_handler)
    
    logger.info(f"Created Logger. ({logger_name})")
    
    return logger

def load_environ(_env_path:str, _key_name:str):
    print(f".env Path=\'{_env_path}\'")
    try:
        dotenv.load_dotenv(_env_path, override=True)
        environ_key = os.environ[f'{_key_name}']
    except:
        try:
            print(f'Failed to load {_key_name}(.env).')
            environ_key = input(f' * Enter your {_key_name} below.\n   > ')
            if environ_key == '' or environ_key == None:
                raise Exception(f'Failed to load {_key_name}(.env).')
            with open(_env_path, 'a') as envfile:
                envfile.write(f'{_key_name}={environ_key}\n')
                envfile.close()
            print(f'{_key_name} is stored in .env [{environ_key}].')
        except Exception as e:
            print(f'\n{_key_name} load failed : {e}')
            sys.exit(f'{_key_name} load failed')
    print(f'{_key_name} load successful [{environ_key}]')
    return environ_key

def verify_product(SERIAL_KEY):
    pass

def gen_hash(data:str | None = None) -> str:
    hash_value = md5(data.encode('utf8')).hexdigest()
    return str(hash_value)

def detect_response_error(response:dict):        
    f_response = {
        'detect'  : False,
        'rstType' : None,
        'rstCode' : None,
        'rstMsg'  : None
    }
    
    # Type 1: Normal Response
    if 'response' in response and 'msgHeader' in response['response']:
        msg_header = response['response']['msgHeader']
        rst_code = msg_header.get('resultCode', '-1')
        rst_msg = get_rst_msg(rst_code)
        f_response.update({
            'detect'  : True,
            'rstCode' : rst_code,
            'rstMsg'  : rst_msg,
            'rstType' : 'normal'
        })
    
    # Type 2: Normal Response 2 (weather(weather) api)
    elif 'response' in response and 'header' in response['response']:
        msg_header = response['response']['header']
        rst_code = msg_header.get('resultCode', '-1')
        rst_msg = get_rst_msg(rst_code)
        f_response.update({
            'detect'  : True,
            'rstCode' : rst_code,
            'rstMsg'  : rst_msg,
            'rstType' : 'normal'
        })
    
    # Type 3: OpenAPI Response
    elif 'OpenAPI_ServiceResponse' in response and 'cmmMsgHeader' in response['OpenAPI_ServiceResponse']:
        cmm_msg_header = response['OpenAPI_ServiceResponse']['cmmMsgHeader']
        rst_code = cmm_msg_header.get('resultCode', '-1')
        rst_msg = get_rst_msg(rst_code, 'openapi')
        f_response.update({
            'detect'  : True,
            'rstCode' : rst_code,
            'rstMsg'  : rst_msg,
            'rstType' : 'openapi'
        })
    
    # Type 4: OpenAPI Response 2 (weather(fine dust) api)
    elif 'response' in response and 'header' in response['response']:
        msg_header = response['response']['header']
        rst_code = msg_header.get('resultCode', '-1')
        rst_msg = get_rst_msg(rst_code, 'openapi')
        f_response.update({
            'detect'  : True,
            'rstCode' : rst_code,
            'rstMsg'  : rst_msg,
            'rstType' : 'openapi'
        })
    
    return f_response

def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=1)
        print("[Check_Internet_Connection]", "Connection Error")
        return True
    except:
        print("[Check_Internet_Connection]", "Connection Error")
        return False
    
def text_to_speech(_text):
    api_key = 'AIzaSyBQ5CwmM5_l9VTsOgB1Ih6ej94Aw-I3JDw'
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    data = {
        "input": {
            "text": _text,
        },
        "voice": {
            "languageCode": "ko-KR",
            "name": "ko-KR-Standard-A",
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "pitch": -1.0,
            "speakingRate": 1.0
        },
    }
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            res = response.json()
            audio_content = res["audioContent"]
            
            # base64 디코딩
            audio_data = base64.b64decode(audio_content)
            
            # 파일로 저장
            with open(os.path.join('src', 'audio', 'output.mp3'), "wb") as audio_file:
                audio_file.write(audio_data)
            
            print("[TTS] Output Complete")
        else:
            print(f"[TTS] Status Error: {response.status_code}")
    except Exception as e:
        print(f"[TTS] Error: {e}")