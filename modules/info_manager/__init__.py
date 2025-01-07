import modules.utils as utils
import modules.config as config
import modules.info_manager.apis.bus as bus
import modules.info_manager.apis.weather as weather
import modules.info_manager.apis.everline as everline

class InfoManager:
    def __init__(self, SERVICE_KEY):
        self.everline = everline
        self.everline_api = self.everline.EverlineAPI()
        self.everline_api.start_auto_update(config.OPTIONS['everline']['refreshInterval'])

service = InfoManager(utils.get_env_key('SERVICE_KEY'))
