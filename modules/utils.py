import os
import sys

import logging
import json
import base64
import socket
import uuid
import datetime
import requests
import modules.config as config
from dotenv import load_dotenv
from hashlib import md5
from PIL import Image, ImageDraw, ImageFont


# Variables
log_time_format = "%Z %x %X"
log_format = "%(asctime)s %(levelname)8s %(message)s"
default_timef = "%Y%m%d%H%M%S"
ENV_PATH = os.path.join(os.getcwd(), '.env')

# Excute
load_dotenv(ENV_PATH)

# Functions
def get_env_key(key_name: str) -> dict:
    value = os.getenv(key_name)
    if value is None:
        raise ValueError(f"Key Error: {key_name}")
        
    return value

def gen_hash() -> str:
    random_uuid = uuid.uuid4()
    hash_value = md5(random_uuid.bytes).hexdigest()
    return str(hash_value)

def get_mac_address() -> str:
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)])
    return mac

def get_now_iso_time() -> str:
    return datetime.datetime.now().isoformat()

def get_now_ftime(format: str = default_timef) -> str:
    return datetime.datetime.now().strftime(format)

def get_ip(default: str = "N/A", ext_ip: str = '1.1.1.1') -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((ext_ip, 80))
            ip_address = s.getsockname()[0]
    except Exception as e:
        ip_address = default
    return ip_address

def check_internet_connection(_timeout:int=1):
    try:
        requests.get("http://www.google.com", timeout=_timeout)
        return True
    except Exception as e:
        return False

def get_text_volume(text, font) -> int:
    dummy_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]  # Right - Left
    return text_width

def get_text_align_space(_width, _text, _font) -> tuple:
    return int( (_width - get_text_volume(_text, _font)) / 2 )

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