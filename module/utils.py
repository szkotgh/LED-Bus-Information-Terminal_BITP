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
log_format = "%(asctime)s %(levelname)8s %(message)s"
default_timef = "%Y%m%d%H%M%S"

normal_api_code = {
    "0"  : "정상적으로 처리되었습니다.",
    "1"  : "시스템 에러가 발생하였습니다.",
    "2"  : "필수 요청 Parameter 가 존재하지 않습니다.",
    "3"  : "필수 요청 Parameter 가 잘못되었습니다.",
    "4"  : "결과가 존재하지 않습니다.",
    "5"  : "필수 요청 Parameter(인증키) 가 존재하지 않습니다.",
    "6"  : "등록되지 않은 키입니다.",
    "7"  : "사용할 수 없는(등록은 되었으나, 일시적으로 사용 중지된) 키입니다.",
    "8"  : "요청 제한을 초과하였습니다.",
    "20" : "잘못된 위치로 요청하였습니다. 위경도 좌표값이 정확한지 확인하십시오.",
    "21" : "노선번호는 1자리 이상 입력하세요.",
    "22" : "정류소명/번호는 1자리 이상 입력하세요.",
    "23" : "버스 도착 정보가 존재하지 않습니다.",
    "31" : "존재하지 않는 출발 정류소 아이디(ID)/번호입니다.",
    "32" : "존재하지 않는 도착 정류소 아이디(ID)/번호입니다.",
    "99" : "API 서비스 준비중입니다.",
}

openapi_error_code = {
    "00": ["NORMAL_SERVICE", "정상"],
    "01": ["APPLICATION_ERROR", "어플리케이션 에러"],
    "02": ["DB_ERROR", "데이터베이스 에러"],
    "03": ["NODATA_ERROR", "데이터없음 에러"],
    "04": ["HTTP_ERROR", "HTTP 에러"],
    "05": ["SERVICETIME_OUT", "서비스 연결실패 에러"],
    "10": ["INVALID_REQUEST_PARAMETER_ERROR", "잘못된 요청 파라메터 에러"],
    "11": ["NO_MANDATORY_REQUEST_PARAMETERS_ERROR", "필수요청 파라메터가 없음"],
    "12": ["NO_OPENAPI_SERVICE_ERROR", "해당 오픈API서비스가 없거나 폐기됨"],
    "20": ["SERVICE_ACCESS_DENIED_ERROR", "서비스 접근거부"],
    "21": ["TEMPORARILY_DISABLE_THE_SERVICEKEY_ERROR", "일시적으로 사용할 수 없는 서비스 키"],
    "22": ["LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR", "서비스 요청제한횟수 초과에러"],
    "30": ["SERVICE_KEY_IS_NOT_REGISTERED_ERROR", "등록되지 않은 서비스키"],
    "31": ["DEADLINE_HAS_EXPIRED_ERROR", "기한만료된 서비스키"],
    "32": ["UNREGISTERED_IP_ERROR", "등록되지 않은 IP"],
    "33": ["UNSIGNED_CALL_ERROR", "서명되지 않은 호출"],
    "99": ["UNKNOWN_ERROR", "기타에러"],
}

def get_now_ftime(time_format: str | None = default_timef) -> str:
    time = datetime.datetime.now()
    f_time = time.strftime(time_format)
    return f_time

def get_now_iso_time() -> str:
    time = datetime.datetime.now()
    return time.isoformat()

def parse_time(ftime_str: str, time_format: str | None = default_timef) -> datetime.datetime:
    time = datetime.datetime.strptime(ftime_str, time_format)
    return time

def get_ip(_defalut:str = "N/A") -> str:
    try:
        if os.name == 'nt':
            ip = subprocess.check_output(['ipconfig']).decode('utf-8').split('\n')
            ip_address = ip[14].split(':')[-1].strip() if ip else _defalut
        else:
            ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').split(' ')
            ip_address = ip[0] if ip else _defalut
        ip_address = ip if ip else _defalut
    except Exception:
        ip_address = _defalut
    
    return ip_address

def chunk_list(lst: list, _chunk_size=3) -> list:
    return [lst[i:i + _chunk_size] for i in range(0, len(lst), _chunk_size)]

def create_logger(logger_name, logger_file_path=None, logger_set_level=logging.DEBUG, file_set_level=logging.DEBUG) -> logging.Logger:    
    if not os.path.exists(os.path.join(os.getcwd(), 'log')):
        os.makedirs(os.path.join(os.getcwd(), 'log'), exist_ok=True)
    
    if logger_file_path == None:
        logger_file_path = os.path.join(os.getcwd(), 'log', f'{logger_name}.log')
    
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
    
    logger.info(f"Logging start. [{logger_name}]")
    
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

def verify_product(_SERIAL_KEY):
    pass

def gen_hash(_data:str | None = None) -> str:
    hash_value = md5(_data.encode('utf8')).hexdigest()
    return str(hash_value)

def detect_response_error(_res_dict:dict, _df_code:str='-1', _df_msg:str='Unknown Error') -> tuple:     
    'return: (res_code, res_msg)'
    
    # Normal Response
    if "response" in _res_dict and "msgHeader" in _res_dict["response"]:
        res_code = _res_dict["response"]["msgHeader"]["resultCode"]
        res_msg  = _res_dict["response"]["msgHeader"]["resultMessage"]
        return (res_code, res_msg)
    
    # Findust Response
    elif "response" in _res_dict and "header" in _res_dict["response"]:
        res_code = _res_dict["response"]["header"]["resultCode"]
        res_msg  = _res_dict["response"]["header"]["resultMsg"]
        return (res_code, res_msg)
    
    # Weather Response
    elif "response" in _res_dict and "body" in _res_dict["response"]:
        res_code = _res_dict["response"]["body"]["header"]["resultCode"]
        res_msg  = _res_dict["response"]["body"]["header"]["resultMsg"]
        return (res_code, res_msg)
    
    # OpenAPI Response
    elif "OpenAPI_ServiceResponse" in _res_dict and "cmmMsgHeader" in _res_dict["OpenAPI_ServiceResponse"]:
        res_code = _res_dict["OpenAPI_ServiceResponse"]["cmmMsgHeader"]["returnReasonCode"]
        res_msg  = _res_dict["OpenAPI_ServiceResponse"]["cmmMsgHeader"]["errMsg"]
        return (res_code, res_msg)
    
    # Unknown Response
    else:
        return (_df_code, _df_msg)

def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=1)
        print("[Check_Internet_Connection]", "Connection Success")
        return True
    except Exception as e:
        print("[Check_Internet_Connection]", f"Connection Error: {e}")
        return False