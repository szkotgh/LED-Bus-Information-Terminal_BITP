import os
import logging
from hashlib import md5
import datetime

default_time_format = '%M.%f'

def get_now_ftime(time_format: str | None = default_time_format) -> str:
    time = datetime.datetime.now()
    f_time = time.strftime(time_format)
    return f_time

def convert_ftime(ftime_str: str, time_format: str | None = default_time_format) -> datetime.datetime:
    time = datetime.datetime.strptime(ftime_str, time_format)
    return time

def create_logger(logger_file_path, logger_set_level=logging.DEBUG, file_set_level=logging.DEBUG) -> logging.Logger:
    logger_file_path = logger_file_path
    logger_set_level = logger_set_level
    file_set_level = file_set_level
    
    logger = logging.getLogger()
    logger.setLevel(logger_set_level)
    formatter = logging.Formatter("[%(levelname)s|%(name)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s", datefmt="%Y%m%d|%H%M%S")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(logger_file_path, 'w', encoding='UTF-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_set_level)
    logger.addHandler(file_handler)
    
    return logger

def gen_hash(data:str | None = None) -> str:
    hash_value = md5(data.encode('utf8')).hexdigest()
    return str(hash_value)
