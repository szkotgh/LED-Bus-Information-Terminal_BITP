import os
import sys
import multiprocessing
import time
import json
import subprocess

# import module.utils
try:
    import module.utils as utils
except Exception as e:
    sys.exit(f'module.utils module import failed : {e}')
# import module.info_manager
try:
    from module.info_manager import InfoManager
except Exception as e:
    sys.exit(f'module.bus_manager module import failed : {e}')
# import module.matrix_manager
try:
    from module.matrix_manager import MatrixManager
except Exception as e:
    sys.exit(f'module.matrix_manager module import failed : {e}')
# import module.speaker_manager
try:
    from module.speaker_manager import SpeakerManager
except Exception as e:
    sys.exit(f'module.speaker_manager module import failed : {e}')

# option load
try:
    with open(os.path.join(os.getcwd(), 'src', 'option.json'), 'r', encoding='UTF-8') as f:
        OPTIONS = json.loads(f.read())
except Exception as e:
    sys.exit(f'option.json load failed : {e}')
    
# prct_info load
try:
    with open(os.path.join(os.getcwd(), 'src', '.prct_info.json'), 'r', encoding='UTF-8') as f:
        REGI_OPTIONS = json.loads(f.read())
except Exception as e:
    sys.exit(f'prct_info.json load failed : {e}')

# get service key
ENV_PATH = os.path.join(os.getcwd(), 'src', '.env')
SERVICE_KEY = utils.load_environ(ENV_PATH, 'SERVICE_KEY')
GOOGLE_KEY = utils.load_environ(ENV_PATH, 'GOOGLE_KEY')
SERIAL_KEY = utils.load_environ(ENV_PATH, 'SERIAL_KEY')
logger = utils.create_logger('bitp_app')

# program start
info_manager = InfoManager(SERVICE_KEY, OPTIONS)
matrix_manager = MatrixManager()
speaker_manager = SpeakerManager()
f_serialKey = '-'.join([SERIAL_KEY[i:i+4] for i in range(0, len(SERIAL_KEY), 4)])
logger.info(f"start BITP")
print(f"prdc_id: {f_serialKey}")
# for i in range(100, -1, -1):
#     sec_str = i/10
#     if sec_str >= 5:
#         sec_str = int(sec_str)
#     matrix_manager.show_text_page([f"BIT가 시작됩니다 . . . ({sec_str}s)", "", f"{utils.get_now_ftime()}", f"IP={utils.get_ip()}", f"(v2.1.16) {f_serialKey}"], 0, 0.1, _status_prt=False)

# # show test page
# matrix_manager.show_test_page(0, 1)
# matrix_manager.show_test_page(1, 3)
# matrix_manager.show_test_page(2, 3)

matrix_manager.show_text_page(["정보를 불러오는 중입니다 . . . "])
info_manager.update_all_info()

# # etc print
# matrix_manager.show_text_page(["한국환경공단 에어코리아 대기오염 정보", "데이터는 실시간 관측된 자료이며, 측정소 현지 사정이나 데이터의 수신상태에 따라 미수신 될 수 있음.", "", "", "출처/데이터 오류 가능성 고지"], _status_prt=False)

# show main content
matrix_manager.update_station_info(info_manager.station_datas)
while 1:
    for i in range(0, len(info_manager.station_datas)):
        for _repeat in range(0, 3):
            matrix_manager.check_internet_connection()
            # try: 
            matrix_manager.show_station_page(i)
            # except Exception as e: matrix_manager.show_text_page(["SHOW STATION PAGE", "에러가 발생하였습니다.", "", f"{utils.get_now_iso_time()}", f"{e}"], _repeat=2); print(f"SHOW STATION PAGE ERROR: {e}")
            try: matrix_manager.show_station_etc_page(i)
            except Exception as e: matrix_manager.show_text_page(["SHOW STATION ETC PAGE", "에러가 발생했습니다.", "", f"{utils.get_now_iso_time()}", f"{e}"], _repeat=2); print(f"SHOW STATION ETC PAGE ERROR: {e}")
    print("ROOF END")
    
print()
print('PROGRAM ENDED')

