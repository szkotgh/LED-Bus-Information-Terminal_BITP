import os
import logging
from hashlib import md5
import datetime

log_format = "[%(levelname)s|%(name)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s"
default_time_format = "%M . %f"

def get_now_ftime(time_format: str | None = default_time_format) -> str:
    time = datetime.datetime.now()
    f_time = time.strftime(time_format)
    return f_time

def convert_ftime(ftime_str: str, time_format: str | None = default_time_format) -> datetime.datetime:
    time = datetime.datetime.strptime(ftime_str, time_format)
    return time

def create_logger(logger_name, logger_file_path=os.path.join('log', 'mainlog.log'), logger_set_level=logging.DEBUG, file_set_level=logging.DEBUG) -> logging.Logger:    
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_set_level)
    formatter = logging.Formatter(log_format, datefmt="%Y%m%d|%H%M%S")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(logger_file_path, 'a', encoding='UTF-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_set_level)
    logger.addHandler(file_handler)
    
    return logger

def gen_hash(data:str | None = None) -> str:
    hash_value = md5(data.encode('utf8')).hexdigest()
    return str(hash_value)

def detect_response_error(response:dict):        
    f_response = {
        'error'   : False,
        'rstType' : None,
        'rstCode' : None,
        'rstMsg'  : None
    }
    
    # Type 1: Normal Response
    if 'response' in response and 'msgHeader' in response['response']:
        msg_header = response['response']['msgHeader']
        f_response['error']   = True
        f_response['rstCode'] = msg_header.get('resultCode', None)
        f_response['rstMsg']  = msg_header.get('resultMessage', None)
        f_response['rstType'] = 'normal'
    
    # Type 2: Normal Response 2 (weather api)
    elif 'response' in response and 'header' in response['response']:
        msg_header = response['response']['header']
        f_response['error']   = True
        f_response['rstCode'] = msg_header.get('resultCode', None)
        f_response['rstMsg']  = msg_header.get('resultMessage', None)
        f_response['rstType'] = 'normal'
    
    # Type 2: OpenAPI Response
    elif 'OpenAPI_ServiceResponse' in response and 'cmmMsgHeader' in response['OpenAPI_ServiceResponse']:
        cmm_msg_header = response['OpenAPI_ServiceResponse']['cmmMsgHeader']
        f_response['error']   = True
        f_response['rstCode'] = cmm_msg_header.get('returnReasonCode', None)
        f_response['rstMsg']  = cmm_msg_header.get('returnAuthMsg', None)
        f_response['rstType'] = 'openapi'
    
    return f_response