import base64
import threading
import time
import queue
import pygame
import requests

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
        
        audio_data = response.json()['audioContent']
        with open('src/tts.mp3', 'wb') as f:
            f.write(base64.b64decode(audio_data))
            
        self.add_notification('audio/tts.mp3')
    
    def run_audio(self):
        pygame.mixer.init()
        while True:
            if not self.audio_queue.empty():
                current_path = self.audio_queue.get()
                self.play_audio(current_path, is_notification=False)
            else:
                time.sleep(1)
    
    def run_notification(self):
        pygame.mixer.init()
        while True:
            if not self.notification_queue.empty():
                current_path = self.notification_queue.get()
                self.is_notificating = True
                self.play_audio(current_path, is_notification=True)
                self.is_notificating = False
            else:
                time.sleep(1)

    def play_audio(self, path, is_notification):
        if is_notification:
            notification_channel = pygame.mixer.Channel(1)
            notification_channel.set_volume(self.notification_volume)
            notification_channel.play(pygame.mixer.Sound(path))
            while notification_channel.get_busy():
                notification_channel.set_volume(self.notification_volume)
                time.sleep(0.1)
        else:
            audio_channel = pygame.mixer.Channel(0)
            audio_channel.set_volume(self.audio_volume)
            audio_channel.play(pygame.mixer.Sound(path))
            while audio_channel.get_busy():
                if self.is_notificating:
                    audio_channel.set_volume(self.notificating_audio_volume)
                else:
                    audio_channel.set_volume(self.audio_volume)
                time.sleep(0.1)
                
master = AudioManager()