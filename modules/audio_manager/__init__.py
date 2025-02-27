import base64
import threading
import time
import queue
import pygame
import requests
import os

TTS_TEMP_PATH = './temp_tts.mp3'

class AudioManager:
    def __init__(self):
        
        self.audio_queue = queue.Queue()
        self.audio_volume = 1
        
        self.notification_queue = queue.Queue()
        self.notification_volume = 1
        self.notificating_audio_volume = 0.3
        self.is_notificating = False
        
        self.audio_thread = threading.Thread(target=self.run_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        self.notification_thread = threading.Thread(target=self.run_notification)
        self.notification_thread.daemon = True
        self.notification_thread.start()

    def add_audio_path(self, _path):
        self.audio_queue.put(_path)
        
    def add_notification(self, _path):
        self.notification_queue.put(_path)

    def tts_play(self, _text, _GOOGLE_API_KEY):
        response = requests.post(
            'https://texttospeech.googleapis.com/v1/text:synthesize',
            headers={
                'X-Goog-Api-Key': _GOOGLE_API_KEY,
                'Content-Type': 'application/json'
            },
            json={
                'input': {
                    'text': _text
                },
                'voice': {
                    "languageCode": "ko-KR",
                    "name": "ko-KR-Wavenet-A",
                    "ssmlGender": "FEMALE"
                },
                'audioConfig': {
                    "audioEncoding": "MP3",
                    "speakingRate": 0.9,
                    "pitch": -3.0,
                    "volumeGainDb": 0.0,
                    "sampleRateHertz": 24000,
                    "effectsProfileId": ["headphone-class-device"]
                }
            }
        )

        response_data = response.json()
        if 'audioContent' not in response_data:
            print("TTS 생성 실패:", response_data)
            return
        
        audio_data = response_data['audioContent']
        
        with open(TTS_TEMP_PATH, 'wb') as f:
            f.write(base64.b64decode(audio_data))
        
        # wait until file is created
        while not os.path.exists(TTS_TEMP_PATH):
            time.sleep(0.1)
        
        self.add_notification(TTS_TEMP_PATH)
    
    def run_audio(self):
        while True:
            if not self.audio_queue.empty():
                current_path = self.audio_queue.get()
                self.play_audio(current_path, is_notification=False)
            else:
                time.sleep(1)
    
    def run_notification(self):
        while True:
            if not self.notification_queue.empty():
                current_path = self.notification_queue.get()
                self.is_notificating = True
                self.play_audio(current_path, is_notification=True)
                self.is_notificating = False
            else:
                time.sleep(1)

    def play_audio(self, path, is_notification):
        if not os.path.exists(path):
            print(f"오류: 파일 {path} 이(가) 존재하지 않습니다.")
            return
        
        sound = pygame.mixer.Sound(path)

        if is_notification:
            notification_channel = pygame.mixer.Channel(1)
            notification_channel.set_volume(self.notification_volume)
            notification_channel.play(sound)
            
            while notification_channel.get_busy():
                notification_channel.set_volume(self.notification_volume)
                time.sleep(0.1)
        else:
            audio_channel = pygame.mixer.Channel(0)
            audio_channel.set_volume(self.audio_volume)
            audio_channel.play(sound)

            while audio_channel.get_busy():
                if self.is_notificating:
                    audio_channel.set_volume(self.notificating_audio_volume)
                else:
                    audio_channel.set_volume(self.audio_volume)
                time.sleep(0.1)
                
service = AudioManager()
