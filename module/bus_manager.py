
import os
import sys
import json
import logging
import datetime

# import module.api_modules.bus
try:
    import module.api_modules.bus as bus
except Exception as e:
    sys.exit(f'module.api_modules.bus module import failed : {e}')
# import module.utils
try:
    import module.utils as utils
except Exception as e:
    sys.exit(f'module.utils module import failed : {e}')

class bus_info_refresh_manager:
    def __init__(self, SERVICE_KEY):
        # logger_set
        logger_path = os.path.join(os.getcwd(), 'log', 'bus_manager.log')
        logger_set_level = logging.DEBUG
        file_set_level = logging.DEBUG
        self.logger = utils.create_logger(logger_path, logger_set_level, file_set_level)

        self.logger.info(f'Logging start {__class__}')
        
        # init class
        self.SERVICE_KEY = SERVICE_KEY
        self.max_retry_api_error = 10
        self.station_list = []
        self.bus_api_mgr = bus.bus_api_requester(self.SERVICE_KEY)
        
        if self.max_retry_api_error < 0:
            self.logger.error("\'retry_max_api_error\' value cannot be lower than 0.")
            sys.exit(1)
        
        self.regi_station_list_path = os.path.join(os.getcwd(), 'src', 'busStaList.json')
        self.regi_station_list = {}
        self.station_list = []
        try:
            with open(self.regi_station_list_path, 'r', encoding='UTF-8') as bus_station_list:
                self.regi_station_list = json.loads(bus_station_list.read())
            self.regi_station_list['busStationList']
            for regi_station in self.regi_station_list['busStationList']:
                self.station_list.append({
                    'keyword'     : regi_station['keyword'],
                    'stationDesc' : regi_station['stationDesc'],
                    'stationInfo' : None,
                    'arvlBusInfo' : None
                })
        except FileNotFoundError as e:
            self.logger.error(f'FileNotFoundError. Check the file \'{self.regi_station_list_path}\' : {e}')
            sys.exit(1)
        except json.JSONDecodeError as e:
            self.logger.error(f'JSONDecodeError. Check the file \'{self.regi_station_list_path}\' : {e}')
            sys.exit(1)
        except KeyError as e:
            self.logger.error(f'KeyError. Check the file \'{self.regi_station_list_path}\' : {e}')
            sys.exit(1)
        except Exception as e:
            self.logger.error(f'Unknown Error. Check the file \'{self.regi_station_list_path}\' : {e}')
            sys.exit(1)
            
        self.logger.info(f"Regi station list: {self.regi_station_list}")
    
    def update_station_info(self) -> None:
        '''
station_list 정보 갱신 함수
---------------------------
bus info refresh manager 객체 내부 station_list 값 갱신 함수.\n
저장된 역 정보를 갱신합니다.
        '''
        
        self.logger.info("[UpdateStationInfo] - Start updating . . .")
        num = 1
        for station in self.station_list:
            update_succes = False
            station_info_rst = None
            
            for try_count in range(0, self.max_retry_api_error+1):
                if try_count == self.max_retry_api_error:
                    self.logger.error(f"[UpdateStationInfo] - api_request_fail updateStationInfo[{station['keyword']}]")
                    station_info_rst = None
                    break
                
                station_info_rst = self.bus_api_mgr.get_station_info(station['keyword'])
                
                if station_info_rst == None:
                    self.logger.warning(f"[UpdateStationInfo] - api_request_fail_retry.. ({try_count+1}/{self.max_retry_api_error}) updateStationInfo[{station['keyword']}]")
                    continue
                
                update_succes = True        
                break
            
            station['stationInfo'] = station_info_rst
            
            if update_succes == True:
                self.logger.info(f"[UpdateStationInfo] - Updated ({num}/{len(self.regi_station_list['busStationList'])})")
            else:
                self.logger.info(f"[UpdateStationInfo] - Update Fail ({num}/{len(self.regi_station_list['busStationList'])})")
            
            num += 1
        
        self.logger.info("[UpdateStationInfo] - Updating complete")
        
        return 0;
        
    def update_station_arvl_bus_info(self):
        '''
station_list 하위 곧 도착 버스 목록 갱신 함수
---------------------------------------------
station_list 하위 arvlbusResult 객체 갱신 함수.
곧 도착 버스 정보를 갱신합니다.
        '''
        
        self.logger.info("[UpdateStationArvlBusInfo] - Start updating . . .")
        num=1
        for station in self.station_list:
            update_succes = False
            arvl_bus_rst = None
            
            if station['stationInfo']['apiSuccess'] == False:
                station['arvlBusInfo'] = None
                continue
            
            for try_count in range(0, self.max_retry_api_error+1):
                if try_count == self.max_retry_api_error:
                    self.logger.error(f"[UpdateStationArvlBusInfo] - api_request_fail UpdateStationArvlBusInfo[{station['keyword']}]")
                    arvl_bus_rst = None
                    break
                
                arvl_bus_rst = self.bus_api_mgr.get_bus_arrival(station['stationInfo']['result']['stationId'])
                
                if arvl_bus_rst == None:
                    self.logger.warning(f"[UpdateStationArvlBusInfo] - api_request_fail_retry.. ({try_count+1}/{self.max_retry_api_error}) UpdateStationArvlBusInfo[{station['keyword']}]")
                    continue
                
                update_succes = True
                break
            
            station['arvlBusInfo'] = arvl_bus_rst
            
            if update_succes == True:
                self.logger.info(f"[UpdateStationArvlBusInfo] - Updated ({num}/{len(self.station_list)})")
            else:
                self.logger.info(f"[UpdateStationArvlBusInfo] - Update Fail ({num}/{len(self.station_list)})")
            
            num += 1
        
        self.logger.info("[UpdateStationArvlBusInfo] - Updating complete")
        
        return 0;