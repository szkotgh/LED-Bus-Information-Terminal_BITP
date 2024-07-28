import os
import sys
import json
import logging
from datetime import datetime, timedelta

# import module.api_modules.bus
try:
    import module.api_modules.weather as weather_api
except Exception as e:
    sys.exit(f'module.api_modules.bus module import failed : {e}')
# import module.utils
try:
    import module.utils as utils
except Exception as e:
    sys.exit(f'module.utils module import failed : {e}')
    
class weather_info_manager:
    def __init__(self, SERVICE_KEY):
        # set logger
        logger_name = "weather_mgr"
        logger_path = os.path.join(os.getcwd(), 'log', 'mainlog.log')
        logger_set_level = logging.DEBUG
        file_set_level = logging.DEBUG
        self.logger = utils.create_logger(logger_name, logger_path, logger_set_level, file_set_level)

        self.logger.info(f'Logging start {__class__}')
        
        # init class
        self.SERVICE_KEY = SERVICE_KEY
        self.max_retry_api_error = 10
        self.tomorrow_weather_info = []
        self.weather_api_mgr = weather_api.weather_api_requester(SERVICE_KEY)
        
        if self.max_retry_api_error < 0:
            self.logger.error("\'retry_max_api_error\' value cannot be lower than 0.")
            sys.exit(1)
        
    def update_weather_info(self):
        base_time = ['0200', '0500', '0800', '1100', '1400', '1700', '2000', '2300']
        
        now = datetime.now()
        now_date = now.strftime("%Y%m%d") # YYYYMMDD
        now_time = now.strftime("%H%M")   # HHMM
        
        tomorrow = now + timedelta(days=1)
        tomorrow_date = tomorrow.strftime("%Y%m%d") # YYYYMMDD
        tomorrow_time = tomorrow.strftime("%H%M")   # HHMM
        
        sel_base_time = min(base_time, key=lambda t: abs(int(now_time) - int(t)))
        
        response = self.weather_api_mgr.get_vilage_fcst("36", "127", now_date, sel_base_time)
        
        # with open(os.path.join('log', 'weather.log'), 'w', encoding='UTF-8') as log:
        #     log.write(json.dumps(response, indent=4))
        
        if response.get('apiSuccess', False) == False:
            print("Error")
            sys.exit(1)
            
        print(type(response.get('result', None)))