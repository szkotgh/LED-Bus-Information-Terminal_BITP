
import os
import sys
import json
import logging
try:
    import module.api_modules.bus as bus
except:
    sys.exit("module.api_modules.bus module Not found")

class bus_info_refresh_manager:
    def __init__(self, SERVICE_KEY):
        self.SERVICE_KEY = SERVICE_KEY
        self.station_list = {}
        
        self.bus_api_mgr = bus.bus_api_requester(self.SERVICE_KEY)
        
        self.regi_station_list_path = os.path.join(os.getcwd(), 'src', 'busStaList.json')
        self.regi_station_list = {None}
        try:
            with open(self.regi_station_list_path, 'r') as bus_station_list:
                self.regi_station_list = json.loads(bus_station_list.read())
            self.regi_station_list['busStationList']
        except KeyError:
            print(f" ! {self.regi_station_list_path} KeyError")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f" ! {self.regi_station_list_path} JSONDecodeError")
            sys.exit(1)
        except FileNotFoundError:
            print(f" ! {self.regi_station_list_path} FileNotFoundError")
            sys.exit(1)
    
    def update_station_info(self) -> None:
        '''
station_list 정보 갱신 함수
---------------------------
bus info refresh manager 객체 내부 station_list 값 갱신 함수.\n
저장된 역 정보를 갱신합니다.
        '''
        print(" * Registered station List")
        col = 1
        for regi_station in self.regi_station_list.get('busStationList', None):
            print(f"   {col}. {regi_station}")
            col += 1
        
        print(self.bus_api_mgr.get_station_info(47312))
        
        return 0;
        