import os
import sys
import json
import logging
from datetime import datetime, timedelta

# import module.utils
try:
    import module.utils as utils
except Exception as e:
    sys.exit(f'module.utils module import failed : {e}')
# import module.api_modules.bus
try:
    import module.api_modules.bus as bus_api
except Exception as e:
    sys.exit(f'module.api_modules.bus module import failed : {e}')
# import module.api_modules.weather
try:
    import module.api_modules.weather as weather_api
except Exception as e:
    sys.exit(f'module.api_modules.bus module import failed : {e}')

# info_manager class
class InfoManager:
    def __init__(self, _SERVICE_KEY, _OPTIONS:dict):
        # Set logger
        logger_name = "info_mgr"
        logger_path = os.path.join(os.getcwd(), 'log', 'mainlog.log')
        logger_set_level = logging.DEBUG
        file_set_level = logging.DEBUG
        self.logger = utils.create_logger(logger_name, logger_path, logger_set_level, file_set_level)
        self.logger.info(f'Logging start. {__class__}')
        
        # Init class
        self.SERVICE_KEY = _SERVICE_KEY
        print(" * InfoManager Regi SERVICE_KEY : ", self.SERVICE_KEY)
        self.OPTIONS = _OPTIONS
        self.API_ERROR_RETRY_COUNT = self.OPTIONS.get('set_api_error_retry_count', 10)
        self.API_TIMEOUT = self.OPTIONS.get('set_api_timeout', 5)
        
        # Bus info init
        self.station_datas = []
        self.bus_api_mgr = bus_api.bus_api_requester(self.SERVICE_KEY)
        
        if self.API_ERROR_RETRY_COUNT < 0:
            self.logger.error("\'retry_max_api_error\' value cannot be lower than 0.")
            sys.exit(1)
        
        self.station_datas = []
        try:
            for station in self.OPTIONS['busStationList']:
                self.station_datas.append({
                    'keyword'          : station['keyword'],
                    'stationDesc'      : station['stationDesc'],
                    'stationInfo'      : None,
                    'arvlBus'          : None,
                    'arvlBusInfo'      : [],
                    'arvlBusRouteInfo' : [],
                    'weatherInfo'      : None,
                    'finedustInfo'     : None
                })
        except Exception as e:
            self.logger.error(f'Failed to load key \'busStationList\'. Check the file \'{_OPTIONS}\' : {e}')
            sys.exit(1)
            
        self.logger.info(f" * Regi station list : {self.station_datas}")
        
        # Weather info init
        self.today_weather_info = []
        self.tomorrow_weather_info = []
        self.tomorrow_need_info = []
        self.weather_api_mgr = weather_api.weather_api_requester(_SERVICE_KEY)
    
    def update_station_info(self) -> None:
        self.logger.info("[UpdateStationInfo] - Start updating . . .")
        num = 0
        for station in self.station_datas:
            num += 1
            
            update_succes = False
            station_info_rst = None
            
            for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                if try_count == self.API_ERROR_RETRY_COUNT:
                    self.logger.error(f"[UpdateStationInfo] - API Request fail. [{station['keyword']}]")
                    station_info_rst = None
                    break
                
                self.logger.info(f"[UpdateStationInfo] - Updating . . . [{station['keyword']}]({num}/{len(self.station_datas)})")
                station_info_rst = self.bus_api_mgr.get_station_info(station['keyword'])
                print(station_info_rst)
                
                if station_info_rst == None:
                    self.logger.warning(f"[UpdateStationInfo] - API Request fail. retry . . . ({try_count+1}/{self.API_ERROR_RETRY_COUNT})[{station['keyword']}]")
                    continue
                
                update_succes = True
                break
            
            if update_succes == False:
                self.logger.info(f"[UpdateStationInfo] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
                
            elif station_info_rst['apiSuccess'] == False:
                self.logger.info(f"[UpdateStationInfo] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
            
            if update_succes == True:
                station['stationInfo'] = station_info_rst
                self.logger.info(f"[UpdateStationInfo] - Updated. [{station['keyword']}]({num}/{len(self.station_datas)})")
        
        self.logger.info("[UpdateStationInfo] - Updating complete.")
        
        return 0;
        
    def update_station_arvl_bus(self):        
        self.logger.info("[UpdateStationArvlBus] - Start updating . . . ")
        num=0
        for station in self.station_datas:
            num += 1
            
            update_succes = False
            arvl_bus_rst = None
            
            if station['stationInfo']['apiSuccess'] == False:
                arvl_bus_rst = None
                continue
            
            for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                if try_count == self.API_ERROR_RETRY_COUNT:
                    self.logger.error(f"[UpdateStationArvlBus] - API Request fail. [{station['keyword']}]")
                    arvl_bus_rst = None
                    break
                
                self.logger.info(f"[UpdateStationArvlBus] - Updating . . . [{station['keyword']}]({num}/{len(self.station_datas)})")
                arvl_bus_rst = self.bus_api_mgr.get_bus_arrival(station['stationInfo']['result']['stationId'])
                
                if arvl_bus_rst == None:
                    self.logger.warning(f"[UpdateStationArvlBus] - API Request fail. retry . . . [{station['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})")
                    continue
                
                update_succes = True
                break
            
            if update_succes == False:
                self.logger.info(f"[UpdateStationArvlBus] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
            
            elif arvl_bus_rst['apiSuccess'] == False:
                self.logger.info(f"[UpdateStationArvlBus] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
                
            if update_succes == True:
                station['arvlBus'] = arvl_bus_rst
                self.logger.info(f"[UpdateStationArvlBus] - Updated. [{station['keyword']}]({num}/{len(self.station_datas)})")
        
        self.logger.info("[UpdateStationArvlBus] - Updating complete.")
        
        return 0;
        
    def update_station_arvl_bus_info(self):        
        self.logger.info("[UpdateStationArvlBusInfo] - Start updating . . . ")
        num=0
        for station in self.station_datas:
            num += 1
            
            if station['arvlBus'] == None or station['arvlBus']['apiSuccess'] == False:
                station['arvlBusInfo'] = None
                self.logger.warning(f"[UpdateStationArvlBusInfo] - Skip. [{station['keyword']}]({num}/{len(self.station_datas)})")
                continue
            
            elif not (station['arvlBus']['rstCode'] in ['0', '00']):
                station['arvlBusInfo'] = None
                self.logger.warning(f"[UpdateStationArvlBusInfo] - Skip. [{station['keyword']}]({num}/{len(self.station_datas)})")
                continue
            
            num_b = 0
            for arvlBus in station['arvlBus']['result']:
                num_b += 1
                
                routeId = arvlBus.get('routeId', None)
                
                if routeId == None:
                    station['arvlBusInfo'].append(None)
                    continue
                
                update_succes = False
                arvl_bus_info_rst = None
                
                for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                    if try_count == self.API_ERROR_RETRY_COUNT:
                        self.logger.error(f"[UpdateStationArvlBusInfo] - API Request fail. [{arvlBus['routeId']}]({num_b}/{len(station['arvlBus']['result'])})[{station['keyword']}]({num}/{len(self.station_datas)})")
                        update_succes = False
                        break
                    
                    self.logger.info(f"[UpdateStationArvlBusInfo] - Updating [{arvlBus['routeId']}]({num_b}/{len(station['arvlBus']['result'])})[{station['keyword']}]({num}/{len(self.station_datas)})")
                    arvl_bus_info_rst = self.bus_api_mgr.get_bus_info(routeId)
                    
                    if arvl_bus_info_rst == None:
                        self.logger.warning(f"[UpdateStationArvlBusInfo] - API Request fail. retry . . . ({try_count+1}/{self.API_ERROR_RETRY_COUNT})({num_b}/{len(station['arvlBus']['result'])})[{arvlBus['routeId']}]({num}/{len(self.station_datas)})[{station['keyword']}]")
                        continue
                    
                    update_succes = True
                    break
                
                if update_succes == False:
                    station['arvlBusInfo'].append(None)
                    self.logger.info(f"[UpdateStationArvlBusInfo] - Update Fail. ({num_b}/{len(station['arvlBus']['result'])})[{arvlBus['routeId']}]({num}/{len(self.station_datas)})[{station['keyword']}]")
                    
                elif arvl_bus_info_rst['apiSuccess'] == False:
                    station['arvlBusInfo'].append(None)
                    self.logger.info(f"[UpdateStationArvlBusInfo] - Update Fail. ({num_b}/{len(station['arvlBus']['result'])})[{arvlBus['routeId']}]({num}/{len(self.station_datas)})[{station['keyword']}]")
                
                if update_succes == True:
                    station['arvlBusInfo'].append(arvl_bus_info_rst)
                    self.logger.info(f"[UpdateStationArvlBusInfo] - Updated. ({num_b}/{len(station['arvlBus']['result'])})[{arvlBus['routeId']}]({num}/{len(self.station_datas)})[{station['keyword']}]")
        
        self.logger.info("[UpdateStationArvlBusInfo] - Updating complete.")
        
        return 0;
    
    def update_station_arvl_bus_route_info(self):
        self.logger.info("[UpdateStationArvlBusRouteInfo] - Start updating . . . ")
        num=0
        for station in self.station_datas:
            num += 1
            
            if self.OPTIONS.get('api_logging', False):
                with open('./log/station.log', 'w', encoding='UTF-8') as f:
                    f.write(json.dumps(station, indent=4))
            
            if station.get('arvlBus', None) == None:
                station['arvlBusRouteInfo'] = None
                self.logger.warning(f"[UpdateStationArvlBusRouteInfo] - Skip. [{station['keyword']}]({num}/{len(self.station_datas)})")
                continue
            
            elif not (station['arvlBus']['rstCode'] in ['0', '006']):
                station['arvlBusRouteInfo'] = None
                self.logger.warning(f"[UpdateStationArvlBusRouteInfo] - Skip. Not a good status code({station['arvlBus']['rstCode']}). [{station['keyword']}]({num}/{len(self.station_datas)})")
                continue
            
            num_b = 0
            for arvlBus in station['arvlBus']['result']:
                num_b += 1
                
                routeId = arvlBus.get('routeId', None)
                
                if routeId == None:
                    station['arvlBusRouteInfo'].append(None)
                    continue
                
                update_succes = False
                arvl_bus_info_rst = None
                
                for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                    if try_count == self.API_ERROR_RETRY_COUNT:
                        self.logger.error(f"[UpdateStationArvlBusRouteInfo] - API Request fail. [{station['keyword']}]")
                        update_succes = False
                        break
                    
                    self.logger.info(f"[UpdateStationArvlBusRouteInfo] - Updating . . . [](/)")
                    arvl_bus_info_rst = self.bus_api_mgr.get_bus_transit_route(routeId)
                    
                    if arvl_bus_info_rst == None:
                        self.logger.warning(f"[UpdateStationArvlBusRouteInfo] - API Request fail. retry . . . [{station['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})")
                        continue
                    
                    update_succes = True
                    break
                
                if update_succes == False:
                    station['arvlBusRouteInfo'].append(None)
                    self.logger.info(f"[UpdateStationArvlBusRouteInfo] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
                    
                elif arvl_bus_info_rst['apiSuccess'] == False:
                    station['arvlBusRouteInfo'].append(None)
                    self.logger.info(f"[UpdateStationArvlBusRouteInfo] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
                
                if update_succes == True:
                    station['arvlBusRouteInfo'].append(arvl_bus_info_rst)
                    self.logger.info(f"[UpdateStationArvlBusRouteInfo] - Updated. [{station['keyword']}]({num}/{len(self.station_datas)})")
        
        self.logger.info("[UpdateStationArvlBusRouteInfo] - Updating complete.")
        
        return 0;
    
    def update_weather_info(self, nx="36", ny="127"):
        self.logger.info(f'[updateWeatherInfo] - Start updating . . . ')
        
        base_time = ['0200', '0500', '0800', '1100', '1400', '1700', '2000', '2300']
        
        today = datetime.now()
        today_date = today.strftime("%Y%m%d") # YYYYMMDD
        today_time = today.strftime("%H%M")   # HHMM
        
        display_time = '0800'
        
        tomorrow = today + timedelta(days=1)
        tomorrow_date = tomorrow.strftime("%Y%m%d") # YYYYMMDD
        tomorrow_time = tomorrow.strftime("%H%M")   # HHMM
        tomorrow_ftime = tomorrow.strftime("%H00")   # HHMM
        
        # Select base time
        sel_base_time = min(base_time, key=lambda t: abs(int(today_time) - int(t)))
        
        num = 0
        for station in self.station_datas:
            num += 1

            if (station.get('stationInfo', None) == None) or (station.get('stationInfo', None).get('apiSuccess', False) == False):
                self.logger.warning(f"[UpdateWeatherInfo] - Skip. [{station['keyword']}]({num}/{len(self.station_datas)})")
                continue
            
            update_succes = False
            weather_rst = None
            
            station_nx = round(float(station['stationInfo']['result']['x']))
            station_ny = round(float(station['stationInfo']['result']['y']))
            
            # Get weather info
            for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                if try_count == self.API_ERROR_RETRY_COUNT:
                    self.logger.error(f"[UpdateWeatherInfo] - API Request fail. [{station['keyword']}]")
                    update_succes = False
                    break
                
                self.logger.info(f"[UpdateWeatherInfo] - Updating . . . [{station['keyword']}]({num}/{len(self.station_datas)})")
                weather_rst = self.weather_api_mgr.get_vilage_fcst(station_nx, station_ny, today_date, sel_base_time)
                
                if weather_rst == None:
                    self.logger.warning(f"[UpdateWeatherInfo] - API Request fail. retry . . . [{station['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})")
                    continue
                
                update_succes = True
                break
            
            if update_succes == False:
                self.logger.info(f"[UpdateWeatherInfo] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
            
            elif weather_rst['apiSuccess'] == False:
                self.logger.info(f"[UpdateWeatherInfo] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
            
            elif update_succes == True:
                # print(f"FFFFFF: {weather_rst}")
                # with open('./log/weather.log', 'w', encoding='UTF-8') as f:
                #     f.write(json.dumps(weather_rst, indent=4))
                
                today_weather_info = []
                tomorrow_weather_info = []
                tomorrow_need_info = []
            
                # Get today and tomorrow weather info
                for item in weather_rst.get('result'):
                    if item.get('fcstDate', None) == today_date:
                        today_weather_info.append(item)
                    elif item.get('fcstDate', None) == tomorrow_date:
                        tomorrow_weather_info.append(item)
                    continue
                
                # Get tomorrow need info
                tomorrow_SKY = None
                tomorrow_PTY = None
                for item in tomorrow_weather_info:
                    if (item.get('category', None) == 'TMN'):
                        tomorrow_need_info.append(item)
                    elif (item.get('category', None) == 'TMX'):
                        tomorrow_need_info.append(item)
                    # 날씨 정보 얻는 부분 개선 필요
                    elif (item.get('category', None) == 'SKY') and (item.get('fcstTime', None) == tomorrow_ftime):
                        tomorrow_need_info.append(item)
                        tomorrow_SKY = item.get('fcstValue', None)
                    elif (item.get('category', None) == 'PTY') and (item.get('fcstTime', None) == tomorrow_ftime):
                        tomorrow_need_info.append(item)
                        tomorrow_PTY = item.get('fcstValue', None)
                
                # Get weather string
                weather_str = None
                if tomorrow_SKY != None and tomorrow_PTY != None:
                    if tomorrow_PTY == '0' or tomorrow_PTY == None:
                        weather_str = weather_api.SKY_info.get(tomorrow_SKY)
                    else:
                        weather_str = weather_api.PTY_info.get(tomorrow_PTY)
                
                tomorrow_need_info.append({
                    'baseDate'  : today_date,
                    'baseTime'  : sel_base_time,
                    'category'  : 'WTS',
                    'fcstDate'  : tomorrow_date,
                    'fcstTime'  : tomorrow_ftime,
                    'fcstValue' : weather_str,
                    'nx'        : nx,
                    'ny'        : ny
                })
                
                weather_rst['result'] = tomorrow_need_info
                station['weatherInfo'] = weather_rst
                
                self.logger.info(f"[UpdateWeatherInfo] - Updated. [{station['keyword']}]({num}/{len(self.station_datas)})")
                        
        self.logger.info("[UpdateWeatherInfo] - Updating complete.")
        return 0
    
    def update_fine_dust_info(self):
        self.logger.info(f'[UpdateFineDustInfo] - Start updating . . . ')
        
        num = 0
        for station in self.station_datas:
            num += 1

            if (station.get('stationInfo', None) == None) or (station.get('stationInfo', None).get('apiSuccess', False) == False):
                self.logger.warning(f"[UpdateFineDustInfo] - Skip. [{station['keyword']}]({num}/{len(self.station_datas)})")
                continue
            
            fine_dust_rst = None
            update_succes = False
            sido_name = '경기'
            admin_dist = '김량장동'
                
            # Get weather info
            for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                if try_count == self.API_ERROR_RETRY_COUNT:
                    self.logger.error(f"[UpdateFineDustInfo] - API Request fail. [{station['keyword']}]")
                    fine_dust_rst = False
                    break
                
                self.logger.info(f"[UpdateFineDustInfo] - Updating . . . [{station['keyword']}]({num}/{len(self.station_datas)})")
                fine_dust_rst = self.weather_api_mgr.get_fine_dust_info(sidoName=sido_name)
                
                if self.OPTIONS.get('api_logging', False):
                    with open(os.path.join('log', 'dust.log'), 'w', encoding="UTF-8") as f:
                        f.write(json.dumps(fine_dust_rst, indent=4))
                
                if fine_dust_rst == None:
                    self.logger.warning(f"[UpdateFineDustInfo] - API Request fail. retry . . . [{station['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})")
                    continue
                
                update_succes = True
                break
            
            if update_succes == False:
                self.logger.info(f"[UpdateFineDustInfo] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
            
            elif fine_dust_rst['apiSuccess'] == False:
                self.logger.info(f"[UpdateFineDustInfo] - Update Fail. [{station['keyword']}]({num}/{len(self.station_datas)})")
        
            if update_succes == True:
                fine_dust_need_info = None
                
                for item in fine_dust_rst['result']:
                    if item['stationName'] == admin_dist:
                        fine_dust_need_info = item
                        break
                    
                fine_dust_rst['result'] = fine_dust_need_info
                station['finedustInfo'] = fine_dust_rst
                
                self.logger.info(f"[UpdateFineDustInfo] - Updated. [{station['keyword']}]({num}/{len(self.station_datas)})")
        
        self.logger.info("[UpdateFineDustInfo] - Updating complete.")
        return 0