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

# Excute
ENV_PATH = os.path.join(os.getcwd(), '.env')
load_dotenv(ENV_PATH)

# Variables
env_file_path = ''
log_time_format = "%Z %x %X"
log_format = "%(asctime)s %(levelname)8s %(message)s"
default_timef = "%Y%m%d%H%M%S"

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

def get_now_time(format: str = default_timef) -> str:
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