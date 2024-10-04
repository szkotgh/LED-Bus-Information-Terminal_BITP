from datetime import datetime
import hashlib
import json
import os
import random
import subprocess

DB_PATH = os.path.join(os.getcwd(), 'db')
FILE_INFO_PATH = os.path.join(os.getcwd(), 'db', 'file_infos.json')
UPLOAD_FOLDER_PATH = os.path.join(os.getcwd(), 'db', 'uploads')
ALLOWED_EXTENSIONS = ['mp4', 'wmv', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif']
LOG_PATH = os.path.join(os.getcwd(), 'log')
LOG_FILE = os.path.join(os.getcwd(), 'log', 'bit-web-server.log')
MAX_UPLOAD_SIZE = 1024 * 1024 * 1024 * 2  # 1GB
MAX_STORAGE = 1024 * 1024 * 1024 * 2  # 1.5GB
SPECIAL_USERID = ['admin', 'gaon']

if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

if not os.path.exists(UPLOAD_FOLDER_PATH):
    os.makedirs(UPLOAD_FOLDER_PATH)

def get_upload_folder_useage() -> int:
    if not os.path.exists(UPLOAD_FOLDER_PATH):
        return 0
    
    return sum(os.path.getsize(os.path.join(UPLOAD_FOLDER_PATH, f)) for f in os.listdir(UPLOAD_FOLDER_PATH) if os.path.isfile(os.path.join(UPLOAD_FOLDER_PATH, f)))

def get_file_infos() -> dict:
    if not os.path.exists(FILE_INFO_PATH):
        return {}
    
    with open(FILE_INFO_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_now_iso_ftime() -> str:
    now = datetime.now()
    return now.isoformat()

def get_now_ftime(_format = '%Y%m%d%H%M%S') -> str:
    now = datetime.now()
    return now.strftime(_format)

def convert_now_ftime(_time_str: str, _format = '%Y%m%d%H%M%S') -> datetime:
    return datetime.strptime(_time_str, _format)

def convert_file_fsize(_size: int) -> str:
    size_unit = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'BB', 'NB', 'DB']
    
    for unit in size_unit:
        if _size < 1024:
            return f'{_size:.2f}{unit}'
        _size /= 1024

def get_local_ip(_defalut:str = "N/A") -> str:
    try:
        ip = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip()
        ip_address = ip if ip else _defalut
    except Exception:
        ip_address = _defalut
    return ip_address

def get_client_ip(request) -> str:
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

def gen_hash(data: str | None = str(random.randbytes)) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()
