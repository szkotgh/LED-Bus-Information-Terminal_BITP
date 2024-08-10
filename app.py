import os
import sys
import multiprocessing
import time
import json
import subprocess

current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
print(current_dir)

# import dotenv
try:
    import dotenv
except Exception as e:
    sys.exit(f'dotenv module import failed : {e}')
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
# # import module.speaker_manager
# try:
#     from module.speaker_manager import SpeakerManager
# except Exception as e:
#     sys.exit(f'module.speaker_manager module import failed : {e}')

# get service key
ENV_PATH = os.path.join(os.getcwd(), 'src', '.env')
SERVICE_KEY = utils.load_environ(ENV_PATH, 'SERVICE_KEY')
GOOGLE_KEY = utils.load_environ(ENV_PATH, 'GOOGLE_KEY')

# get option path
OPTIONS = None
with open(os.path.join(os.getcwd(), 'src', 'option.json'), 'r', encoding='UTF-8') as f:
    OPTIONS = json.loads(f.read())

# program start
info_manager = InfoManager(SERVICE_KEY, OPTIONS)
matrix_manager = MatrixManager()
# speaker_manager = SpeakerManager()

for i in range(100, -1, -1):
    matrix_manager.show_text_page([f"BIT가 시작됩니다 . . . ({(i/10)}s)", "", f"{utils.get_now_ftime()}", f"IP={utils.get_ip()}", f"(v2.1.16) {utils.gen_hash('1234')[:16]}"], 0, 0.1)
# show test page
matrix_manager.show_test_page(0, 1)
matrix_manager.show_test_page(1, 3)
matrix_manager.show_test_page(2, 3)

# with open(os.path.join('log', 'struct.log'), 'r', encoding="UTF-8") as f:
#     info_manager.station_datas = json.loads(f.read())
matrix_manager.show_text_page(["정보를 불러오고 있습니다.", "                                    "], 0, 0)
info_manager.update_station_info()
matrix_manager.show_text_page(["정보를 불러오고 있습니다.", "------                              "], 0, 0)
info_manager.update_station_arvl_bus()
matrix_manager.show_text_page(["정보를 불러오고 있습니다.", "------------                        "], 0, 0)
info_manager.update_station_arvl_bus_info()
matrix_manager.show_text_page(["정보를 불러오고 있습니다.", "------------------                  "], 0, 0)
info_manager.update_station_arvl_bus_route_info()
matrix_manager.show_text_page(["정보를 불러오고 있습니다.", "------------------------            "], 0, 0)
info_manager.update_weather_info()  
matrix_manager.show_text_page(["정보를 불러오고 있습니다.", "------------------------------      "], 0, 0)
info_manager.update_fine_dust_info()
matrix_manager.show_text_page(["정보를 불러오고 있습니다.", "------------------------------------"], 0, 1)

# # show etc print
matrix_manager.show_text_page(["한국환경공단 에어코리아 대기오염 정보", "데이터는 실시간 관측된 자료이며, 측정소 현지 사정이나 데이터의 수신상태에 따라 미수신 될 수 있음.", "", "", "출처/데이터 오류 가능성 고지"])

# show main content
matrix_manager.update_station_info(info_manager.station_datas)
while 1:
    for i in range(0, len(info_manager.station_datas)):
        matrix_manager.show_station_page(i)
    print("ROOF END")
    
print()
print('PROGRAM ENDED')

