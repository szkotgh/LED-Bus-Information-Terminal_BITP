import os
import sys
import multiprocessing
import time

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
# import module.bus_manager
try:
    import module.bus_manager as bus_manager
except Exception as e:
    sys.exit(f'module.bus_manager module import failed : {e}')

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

# program start
bus_mgr = bus_manager.bus_info_refresh_manager(SERVICE_KEY)
bus_mgr.update_station_info()

bus_mgr.update_station_arvl_bus_info()

