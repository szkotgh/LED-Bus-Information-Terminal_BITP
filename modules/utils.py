import os
import sys
import logging
import json
import base64
import socket
from hashlib import md5
import uuid
import dotenv
import datetime
from PIL import Image, ImageDraw, ImageFont
import requests

log_time_format = "%Z %x %X"
log_format = "%(asctime)s %(levelname)8s %(message)s"
default_timef = "%Y%m%d%H%M%S"

def gen_hash(_data:str | None = None) -> str:
    random_uuid = uuid.uuid4()
    hash_value = md5(random_uuid.bytes).hexdigest()
    return str(hash_value)

def check_internet_connection(_timeout:int=1):
    try:
        requests.get("http://www.google.com", timeout=_timeout)
        return True
    except Exception as e:
        return False

def get_ip(default: str = "N/A", ext_ip: str = '1.1.1.1') -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((ext_ip, 80))
            ip_address = s.getsockname()[0]
    except Exception as e:
        ip_address = default
    return ip_address

def get_text_volume(text, font) -> int:
    dummy_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]  # Right - Left
    return text_width