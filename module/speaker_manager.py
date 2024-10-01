import os
import module.utils as utils
import requests

class SpeakerManager:
    def __init__(self, GOOGLE_KEY, _OPTIONS):
        self.logger = utils.create_logger('speaker_manager')
        self.API_KEY = GOOGLE_KEY
        self.tmp_path = '/src/audio'
        self.logger.info(f"tmp_path : {self.tmp_path}")
        
        self.OPTIONS = _OPTIONS
        self.API_ERROR_RETRY_COUNT = self.OPTIONS.get('set_api_error_retry_count', 10)
        self.API_TIMEOUT = self.OPTIONS.get('set_api_timeout', 5)
    
    def reload_option(self, _OPTIONS):
        self.OPTIONS = _OPTIONS
    
    def speak_text(self, text):
        url = "https://texttospeech.googleapis.com/v1beta1/voices"
        response = requests.get(url)
        print(response.text)