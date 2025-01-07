import modules.utils as utils
import modules.config as config

class InfoManager:
    def __init__(self, SERVICE_KEY):
        import modules.info_manager.apis.bus as bus
        import modules.info_manager.apis.weather as weather
        import modules.info_manager.apis.everline as everline
        self.everline = everline.EverlineAPI()
        self.everline.start_auto_update(config.OPTIONS['everline']['refreshInterval'])

info_manager = InfoManager(utils.get_env_key('SERVICE_KEY'))
