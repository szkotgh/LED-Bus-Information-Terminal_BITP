import json
import modules.utils as utils
import modules.config as config
import modules.info_manager.apis.bus as bus
import modules.info_manager.apis.weather as weather
import modules.info_manager.apis.everline as everline
import modules.info_manager.apis.network as network

class InfoManager:
    def __init__(self, SERVICE_KEY):
        self.everline = everline
        self.everline_api = self.everline.EverlineAPI(_req_url=config.OPTIONS['everline']['reqUrl'])
        self.everline_api.start_auto_update(_interval=config.OPTIONS['everline']['refreshInterval'])
        
        self.network = network.NetworkManager(_req_url=config.OPTIONS['network']['reqUrl'], _timeout=config.OPTIONS['api_timeout'])
        self.network.start_auto_update(_interval=config.OPTIONS['network']['refreshInterval'])
        
        with open('./station_datas_struct.json', 'r') as f:
            self.station_datas = json.load(f)

service = InfoManager(utils.get_env_key('SERVICE_KEY'))
