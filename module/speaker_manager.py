import os
import module.utils as utils
import requests

class SpeakerManager:
    def __init__(self, GOOGLE_KEY, _OPTIONS):
        self.API_KEY = GOOGLE_KEY
        self.tmp_path = '/src/audio'
        
        self.load_option(_OPTIONS)
        
        self.logging(f"tmp_path : {self.tmp_path}", "info")

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
        
    def load_option(self, _OPTION):
        self.OPTION = _OPTION
        self.API_ERROR_RETRY_COUNT = self.OPTION['api_error_retry_count']
        self.API_TIMEOUT = self.OPTION['api_timeout']
        
    def speak_text(self, text):
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_KEY}"
        }
        data = {
            "input": {
                "text": text
            },
            "voice": {
                "languageCode": "ko-KR",
                "name": "ko-KR-Wavenet-A"
            },
            "audioConfig": {
                "audioEncoding": "MP3"
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            audio_content = response.json().get('audioContent')
            if audio_content:
                audio_path = os.path.join(self.tmp_path, 'notice.mp3')
                with open(audio_path, 'wb') as audio_file:
                    audio_file.write(audio_content.encode('ISO-8859-1'))
                print("Audio content written to file 'notice.mp3'")
                
                # Play the audio file
                subprocess.run(['mpg123', audio_path])
            else:
                print("No audio content received")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)