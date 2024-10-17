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
    def __init__(self, _SERVICE_KEY, _OPTIONS):
        # Init class
        self.SERVICE_KEY = _SERVICE_KEY
        self.load_option(_OPTIONS)
        self.logging(f" * InfoManager Regi SERVICE_KEY: {self.SERVICE_KEY}")
        self.is_init = False
        self.is_arvl_bus_info_updated = False
        self.is_etc_info_updated = False
        self.station_datas = []
        
        # Bus info init
        self.bus_api_mgr = bus_api.bus_api_requester(self.SERVICE_KEY, _OPTIONS)
        
        # Weather info init
        self.today_weather_info = []
        self.tomorrow_weather_info = []
        self.tomorrow_need_info = []
        self.weather_api_mgr = weather_api.weather_api_requester(self.SERVICE_KEY, _OPTIONS)
    
    def load_option(self, _OPTIONS):
        self.OPTION = _OPTIONS
        self.API_ERROR_RETRY_COUNT = self.OPTION['api_error_retry_count']
        self.API_TIMEOUT = self.OPTION['api_timeout']
    
    def logging(self, str: str, type="info") -> bool:
        if self.OPTION['logging'] == False:
            return False
        
        try:
            self.logger
        except AttributeError:
            self.logger = utils.create_logger('info_manager')
        
        if type == "debug":
            self.logger.debug(str)
        elif type == "info":
            self.logger.info(str)
        elif type == "warning" or type == "warn":
            self.logger.warning(str)
        elif type == "error":
            self.logger.error(str)
        elif type == "critical":
            self.logger.critical(str)
        else:
            self.logger.info(str)
            
        return True
    
    def init_station_datas(self):
        self.station_datas = []
        for station in self.OPTION['busStationList']:
            self.station_datas.append({
                'keyword'          : station['keyword'],
                'stationDesc'      : station['stationDesc'],
                'stationInfo'      : None,
                'arvlBus'          : None,
                'arvlBusInfo'      : [],
                'arvlBusRouteInfo' : [],
                'weatherInfo'      : None,
                'finedustInfo'     : None,
            })
    
    def update_station_info(self) -> None:
        log_title = "UpdateStationInfo"
        
        self.logging(f"[{log_title}] - Start updating . . .", "info")
        
        for station_index, station_data in enumerate(self.station_datas):
            self.station_datas[station_index]['stationInfo'] = None
            update_succes = False
            station_info_rst = None
            
            for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                if try_count == self.API_ERROR_RETRY_COUNT:
                    self.logging(f"[{log_title}] - API Request fail. [{station_data['keyword']}]", "error")
                    break
                
                self.logging(f"[{log_title}] - Updating . . . [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
                station_info_rst = self.bus_api_mgr.get_station_info(station_data['keyword'])
                
                if station_info_rst['errorOcrd'] == True:
                    self.logging(f"[{log_title}] - API Request fail: {station_info_rst['errorMsg']} | retry . . . [{station_data['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
                    continue
                
                update_succes = True
                break
            
            if update_succes == False:
                self.logging(f"[{log_title}] - Update Fail. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
            else:
                self.logging(f"[{log_title}] - Updated. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
            
            # update station info
            self.station_datas[station_index]['stationInfo'] = station_info_rst
        
        self.logging(f"[{log_title}] - Updating process end.", "info")
        
        return update_succes
        
    def update_station_arvl_bus(self):
        log_title = "UpdateStationArvlBus"

        self.logging(f"[{log_title}] - Start updating . . . ", "info")
        
        for station_index, station_data in enumerate(self.station_datas):
            self.station_datas[station_index]['arvlBus'] = None
            
            if station_data['stationInfo']['errorOcrd'] == True or station_data['stationInfo']['apiSuccess'] == False:
                self.logging(f"[{log_title}] - Skip. The data cannot be retrieved. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
                continue
            
            update_succes = False
            arvl_bus_rst = None
            
            for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                if try_count == self.API_ERROR_RETRY_COUNT:
                    self.logging(f"[{log_title}] - API Request fail. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "error")
                    break
                
                self.logging(f"[{log_title}] - Updating . . . [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
                arvl_bus_rst = self.bus_api_mgr.get_bus_arrival(station_data['stationInfo']['result']['stationId'])
                
                if arvl_bus_rst['errorOcrd'] == True:
                    self.logging(f"[{log_title}] - API Request fail: {arvl_bus_rst['errorMsg']} | retry . . . [{station_data['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
                    continue
                
                update_succes = True
                break
            
            if update_succes == False:
                self.logging(f"[{log_title}] - Update Fail. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
            else:
                self.logging(f"[{log_title}] - Updated. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")

            # update arvl bus info
            self.station_datas[station_index]['arvlBus'] = arvl_bus_rst
        
        self.logging(f"[{log_title}] - Updating process end.", "info")
        
        return update_succes
        
    def update_station_arvl_bus_info(self):
        log_title = "UpdateStationArvlBusInfo"
        
        self.logging(f"[{log_title}] - Start updating . . . ", "info")
        
        for station_index, station_data in enumerate(self.station_datas):
            self.station_datas[station_index]['arvlBusInfo'] = []
            
            # Check arvlBus Data
            if station_data['arvlBus']['errorOcrd'] == True or station_data['arvlBus']['apiSuccess'] == False:
                self.logging(f"[{log_title}] - Skip. The data cannot be retrieved. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
                continue
            
            if not station_data['arvlBus']['resCode'] in ["0", "00"]:
                self.logging(f"[{log_title}] - Skip. The data is not in a state where it can be retrieved. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
                continue
            
            # Get arvlBus Infos
            for arvl_index, arvlBus in enumerate(station_data['arvlBus']['result']):
                arvlBus_routeId = arvlBus['routeId']
                
                update_succes = False
                arvl_bus_info_rst = None
                
                for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                    if try_count == self.API_ERROR_RETRY_COUNT:
                        self.logging(f"[{log_title}] - API Request fail. [{arvlBus['routeId']}]({arvl_index+1}/{len(station_data['arvlBus']['result'])})[{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "error")
                        update_succes = False
                        break
                    
                    self.logging(f"[{log_title}] - Updating [{arvlBus['routeId']}]({arvl_index+1}/{len(station_data['arvlBus']['result'])})[{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
                    arvl_bus_info_rst = self.bus_api_mgr.get_bus_info(arvlBus_routeId)
                    
                    if arvl_bus_info_rst['errorOcrd'] == True:
                        self.logging(f"[{log_title}] - API Request fail: {arvl_bus_info_rst['errorMsg']} | retry . . . [{station_data['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
                        continue
                    
                    update_succes = True
                    break
                
                if update_succes == False:
                    self.logging(f"[{log_title}] - Update Fail. ({arvl_index+1}/{len(station_data['arvlBus']['result'])})[{arvlBus['routeId']}]({station_index+1}/{len(self.station_datas)})[{station_data['keyword']}]", "warning")
                else:
                    self.logging(f"[{log_title}] - Updated. ({arvl_index+1}/{len(station_data['arvlBus']['result'])})[{arvlBus['routeId']}]({station_index+1}/{len(self.station_datas)})[{station_data['keyword']}]", "info")
        
                # update arvl bus info
                self.station_datas[station_index]['arvlBusInfo'].append(arvl_bus_info_rst)
                
        self.logging(f"[{log_title}] - Updating process end.", "info")
        
        return update_succes
    
    def update_station_arvl_bus_route_info(self):
        log_title = "UpdateStationArvlBusRouteInfo"
        
        self.logging(f"[{log_title}] - Start updating . . . ", "info")
        
        for station_index, station_data in enumerate(self.station_datas):
            self.station_datas[station_index]['arvlBusRouteInfo'] = []
            
            # Check arvlBus Data
            if station_data['arvlBus']['errorOcrd'] == True or station_data['arvlBus']['apiSuccess'] == False:
                self.station_datas[station_index]['arvlBusRouteInfo'].append(None)
                self.logging(f"[{log_title}] - Skip. The data cannot be retrieved. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
                continue
            
            if not station_data['arvlBus']['resCode'] in ["0", "00"]:
                self.station_datas[station_index]['arvlBusRouteInfo'].append(None)
                self.logging(f"[{log_title}] - Skip. The data is not in a state where it can be retrieved. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
                continue
            
            for arvl_index, arvlBus in enumerate(station_data['arvlBus']['result']):
                arvlBus_routeId = arvlBus.get('routeId', None)
                
                update_succes = False
                arvl_bus_route_info = None
                
                for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                    if try_count == self.API_ERROR_RETRY_COUNT:
                        self.logging(f"[{log_title}] - API Request fail. [{station_data['keyword']}]", "error")
                        update_succes = False
                        break
                    
                    self.logging(f"[{log_title}] - Updating . . . [{station_data['keyword']}]({station_index}/{len(self.station_datas)})", "info")
                    arvl_bus_route_info = self.bus_api_mgr.get_bus_transit_route(arvlBus_routeId)
                    
                    if arvl_bus_route_info['errorOcrd'] == True:
                        self.logging(f"[{log_title}] - API Request fail: {arvl_bus_route_info['errorMsg']} | retry . . . [{station_data['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
                        continue
                    
                    update_succes = True
                    break
                
                if update_succes == False:
                    self.logging(f"[{log_title}] - Update Fail. ({arvl_index+1}/{len(station_data['arvlBus']['result'])})[{arvlBus['routeId']}]({station_index+1}/{len(self.station_datas)})[{station_data['keyword']}]", "warning")
                else:
                    self.logging(f"[{log_title}] - Updated. ({arvl_index+1}/{len(station_data['arvlBus']['result'])})[{arvlBus['routeId']}]({station_index+1}/{len(self.station_datas)})[{station_data['keyword']}]", "info")
                
                self.station_datas[station_index]['arvlBusRouteInfo'].append(arvl_bus_route_info)
        
        self.logging(f"[{log_title}] - Updating process end.", "info")
        
        return update_succes
    
    def update_weather_info(self, nx="36", ny="127"):
        log_title = "UpdateWeatherInfo"
        
        self.logging(f"[{log_title}] - Start updating . . . ", "info")
        
        base_time = ["0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300"]
        
        today = datetime.now()
        today_date = today.strftime("%Y%m%d") # YYYYMMDD
        today_time = today.strftime("%H%M")   # HHMM
        
        display_time = '0800'
        
        tomorrow = today + timedelta(days=1)
        tomorrow_date = tomorrow.strftime("%Y%m%d") # YYYYMMDD
        tomorrow_time = tomorrow.strftime("%H%M")   # HHMM
        tomorrow_ftime = tomorrow.strftime("%H00")  # HHMM
        
        # Select base time
        sel_base_time = min(base_time, key=lambda t: abs(int(today_time) - int(t)))
        
        for station_index, station_data in enumerate(self.station_datas):
            self.station_datas[station_index]['weatherInfo'] = None
            
            # Check arvlBus Data
            if station_data['stationInfo']['errorOcrd'] == True or station_data['stationInfo']['apiSuccess'] == False:
                self.logging(f"[{log_title}] - Skip. The data cannot be retrieved. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
                continue
            
            if not station_data['stationInfo']['resCode'] in ["0", "00"]:
                self.logging(f"[{log_title}] - Skip. The data is not in a state where it can be retrieved. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
                continue
            
            update_succes = False
            weather_rst = None
            
            station_nx = round(float(station_data['stationInfo']['result']['x']))
            station_ny = round(float(station_data['stationInfo']['result']['y']))
            
            # Get weather info
            for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                if try_count == self.API_ERROR_RETRY_COUNT:
                    self.logging(f"[{log_title}] - API Request fail. [{station_data['keyword']}]", "error")
                    update_succes = False
                    break
                
                self.logging(f"[{log_title}] - Updating . . . [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
                weather_rst = self.weather_api_mgr.get_vilage_fcst(station_nx, station_ny, today_date, sel_base_time)
                
                if weather_rst['errorOcrd'] == True:
                    self.logging(f"[{log_title}] - API Request fail: {weather_rst['errorMsg']} | retry . . . [{station_data['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
                    continue
                
                update_succes = True
                break
            
            if update_succes == False:
                self.logging(f"[{log_title}] - Update Fail. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
            
            elif weather_rst['apiSuccess'] == False:
                self.logging(f"[{log_title}] - Update Fail. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
            
            else:
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
                    # ? 날씨 정보 얻는 부분 개선 필요
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
                
                self.station_datas[station_index]['weatherInfo'] = weather_rst
                
                self.logging(f"[{log_title}] - Updated. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
                        
        self.logging(f"[{log_title}] - Updating process end.", "info")
        
        return update_succes
    
    def update_fine_dust_info(self):
        log_title = "UpdateFineDustInfo"
        
        self.logging(f'[{log_title}] - Start updating . . . ', "info")
        
        for station_index, station_data in enumerate(self.station_datas):
            self.station_datas[station_index]['finedustInfo'] = None
            
            if station_data['stationInfo']['errorOcrd'] == True or station_data['stationInfo']['apiSuccess'] == False:
                self.logging(f"[{log_title}] - Skip. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "warning")
                continue
            
            fine_dust_rst = None
            update_succes = False
            sido_name = '경기'
            admin_dist = '김량장동'
                
            # Get weather info
            for try_count in range(0, self.API_ERROR_RETRY_COUNT+1):
                if try_count == self.API_ERROR_RETRY_COUNT:
                    self.logging(f"[{log_title}] - API Request fail. [{station_data['keyword']}]", "error")
                    break
                
                self.logging(f"[{log_title}] - Updating . . . [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
                fine_dust_rst = self.weather_api_mgr.get_fine_dust_info(sidoName=sido_name)
                
                if fine_dust_rst['errorOcrd'] == True:
                    self.logging(f"[{log_title}] - API Request fail. retry . . . [{station_data['keyword']}]({try_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
                    continue
                
                update_succes = True
                break
            
            if update_succes == False:
                self.logging(f"[{log_title}] - Update Fail. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")
            else:
                for fine_dust_item in fine_dust_rst['result']:
                    if fine_dust_item['stationName'] == admin_dist:
                        fine_dust_rst['result'] = fine_dust_item
                        break
                self.logging(f"[{log_title}] - Updated. [{station_data['keyword']}]({station_index+1}/{len(self.station_datas)})", "info")

            self.station_datas[station_index]['finedustInfo'] = fine_dust_rst
        
        self.logging(f"[{log_title}] - Updating process end.", "info")
        
        return update_succes

    def init_info(self):
        log_title = "InitInfo"
        
        self.is_init = False
        self.logging(f"[{log_title}] - Initializing start", "info")
        self.init_station_datas()
        for retry_count in range(0, self.API_ERROR_RETRY_COUNT+1):
            update_rst = self.update_station_info()
            if update_rst == True:
                self.is_init = True
                break
            self.logging(f"[{log_title}] - Update Fail. Retry . . . ({retry_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
        
        if self.is_init == False:
            self.logging(f"[{log_title}] - Initializing Fail.", "error")
            return self.is_init
        self.logging(f"[{log_title}] - Initializing Success.", "info")
        return self.is_init
    
    def init_arvl_bus_info(self):
        log_title = "InitArvlBusInfo"
        
        self.is_arvl_bus_info_updated = False
        self.logging(f"[{log_title}] - Start Initializing . . . ", "info")
        if self.is_init == False:
            self.logging(f"[{log_title}] - Not initialized. Initializing cancel.", "error")
            return False
        
        arvl_bus_updated = False
        for retry_count in range(0, self.API_ERROR_RETRY_COUNT+1):
            update_rst = self.update_station_arvl_bus()
            if update_rst == True:
                arvl_bus_updated = True
                break
            self.logging(f"[{log_title}] - Update Fail. Retry . . . ({retry_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
        if arvl_bus_updated == False:
            self.logging(f"[{log_title}] - Initializing Fail.", "error")
            return False
        
        arvl_bus_route_info_updated = False
        for retry_count in range(0, self.API_ERROR_RETRY_COUNT+1):
            update_rst = self.update_station_arvl_bus_info()
            if update_rst == True:
                arvl_bus_route_info_updated = True
                break
            self.logging(f"[{log_title}] - Update Fail. Retry . . . ({retry_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
        if arvl_bus_route_info_updated == False:
            self.logging(f"[{log_title}] - Initializing Fail.", "error")
            return False
        
        arvl_bus_route_info_updated = False
        for retry_count in range(0, self.API_ERROR_RETRY_COUNT+1):
            update_rst = self.update_station_arvl_bus_route_info()
            if update_rst == True:
                arvl_bus_route_info_updated = True
                break
            self.logging(f"[{log_title}] - Update Fail. Retry . . . ({retry_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
        if arvl_bus_route_info_updated == False:
            self.logging(f"[{log_title}] - Initializing Fail.", "error")
            return False
        
        self.is_arvl_bus_info_updated = True
        self.logging(f"[{log_title}] - Initializing process end.", "info")
        return True
        
    def init_etc_info(self):
        log_title = "InitEtcInfo"
        
        self.is_etc_info_updated = False
        self.logging(f"[{log_title}] - Start Initializing . . . ", "info")
        
        if self.is_init == False:
            self.logging(f"[{log_title}] - Not initialized. Update cancel.", "error")
            return False
        
        fine_dust_info_updated = False
        for retry_count in range(0, self.API_ERROR_RETRY_COUNT+1):
            update_rst = self.update_fine_dust_info()
            if update_rst == True:
                fine_dust_info_updated = True
                break
            self.logging(f"[{log_title}] - Update Fail. Retry . . . ({retry_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
        if fine_dust_info_updated == False:
            self.logging(f"[{log_title}] - Initializing Fail.", "error")
            return False
        
        weather_info_updated = False
        for retry_count in range(0, self.API_ERROR_RETRY_COUNT+1):
            update_rst = self.update_weather_info()
            if update_rst == True:
                weather_info_updated = True
                break
            self.logging(f"[{log_title}] - Update Fail. Retry . . . ({retry_count+1}/{self.API_ERROR_RETRY_COUNT})", "warning")
        if weather_info_updated == False:
            self.logging(f"[{log_title}] - Initializing Fail.", "error")
            return False

        self.is_etc_info_updated = True
        self.logging(f"[{log_title}] - Initializing process end.", "info")
        return True