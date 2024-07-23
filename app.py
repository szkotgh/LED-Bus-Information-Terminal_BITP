import os
import sys
import module.utils as utils
import module.bus_manager as bus_manager
import multiprocessing

try:
    import dotenv
except:
    sys.exit('dotenv module is not installed')

# get service key
SERVICE_KEY = None
ENV_PATH = os.path.join(os.getcwd(), 'src', '.env')
print(f".env Path=\'{ENV_PATH}\'")
try:
    dotenv.load_dotenv(ENV_PATH)
    SERVICE_KEY = os.environ['SERVICE_KEY']
except:
    try:
        print('Failed to load serviceKey(.env).')
        SERVICE_KEY = input(' * Enter your serviceKey below. (Issued after signing up for \'https://data.go.kr\'. Copy Decoding)\n   > ')
        with open(ENV_PATH, 'a') as envfile:
            envfile.write(f'SERVICE_KEY={SERVICE_KEY}\n')
            envfile.close()
        print(f'serviceKey saved. To change the key, edit \'{ENV_PATH}\'.\nIf it does not work properly, check the API usage request below.\n- 경기도 정류소 조회\n- 경기도 버스도착정보 조회\n- 경기도 버스노선 조회\n- 한국환경공단 에어코리아 대기오염정보\n- 기상청 단기예보 ((구) 동네예보) 조회서비스')
    except:
        print('\nserviceKey registration failed')
        sys.exit('serviceKey load failed')
print(f'serviceKey load successful [{SERVICE_KEY}]')

bus_mgr = bus_manager.bus_info_refresh_manager(SERVICE_KEY)
bus_mgr.update_station_info()

bus_mgr.update_station_arvl_bus_info()

for station in bus_mgr.station_list:
    print(station)