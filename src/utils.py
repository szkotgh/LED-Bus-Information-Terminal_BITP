import datetime
import hashlib
import os
import socket
import subprocess

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = ['mp4', 'wmv', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif', 'txt']
LOG_FILE = os.path.join(os.getcwd(), 'log', 'bit-web-server.log')
MAX_STORAGE = 1024 * 1024 * 1024 * 1.5  # 1.5GB

def get_now_iso_ftime() -> str:
    now = datetime.datetime.now()
    return now.isoformat()

def get_now_ftime(_format = '%Y%m%d%H%M%S') -> str:
    now = datetime.datetime.now()
    return now.strftime(_format)

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

def gen_hash(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()
    