import os
import sys
import json
import logging
import modules.utils as utils
import modules.config as config
import modules.info_manager.bus_api as bus_api
import modules.info_manager.weather_api as weather_api

class InfoManager:
    def __init__(self, SERVICE_KEY):
        self.SERVICE_KEY = SERVICE_KEY
        result = weather_api.get_fine_dust_info()
        print(result)
    
    

info_manager = InfoManager(config.SERVICE_KEY)