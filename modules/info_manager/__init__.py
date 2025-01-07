import os
import sys
import json
import logging
import time
import modules.utils as utils
import modules.config as config
import modules.info_manager.apis.bus as bus
import modules.info_manager.apis.weather as weather
import modules.info_manager.apis.everline as everline

class InfoManager:
    def __init__(self, SERVICE_KEY):
        self.everline = everline.EverlineAPI()
        self.everline.start_auto_update(config.OPTIONS['everline']['refreshInterval'])

info_manager = InfoManager(config.SERVICE_KEY)

while True:
    print(info_manager.everline.get_train_info())
    time.sleep(1)