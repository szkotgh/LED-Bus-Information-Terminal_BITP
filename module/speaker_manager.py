import os
import sys
import pygame
import time

class SpeakerManager:
    def __init__(self, music_volume=1, notice_volume=1):
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Error initializing Pygame mixer: {e}")
            sys.exit(1)
        
        current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.notice_effect_path = os.path.join(current_dir, "src/audio/notice_effect.mp3")
        
        self.music_volume = music_volume
        self.notice_volume = notice_volume
        
        self.music = pygame.mixer.music
        self.play_notice_effect = True
        self.notice_effect = pygame.mixer.Sound(self.notice_effect_path)
        self.notice_effect.set_volume(self.notice_volume * 0.8)

        self.current_notice = None

    def fade_volume(self, target_volume, duration, steps=20):
        current_volume = self.music.get_volume()
        step_size = (target_volume - current_volume) / steps
        for _ in range(steps):
            current_volume += step_size
            self.music.set_volume(max(0, min(current_volume, 1)))
            time.sleep(duration / steps)

    def music_play(self, path):
        if self.music.get_busy():
            self.music_stop()
        self.music.load(path)
        self.music.play(-1)
        self.music.set_volume(self.music_volume)

    def music_stop(self):
        self.music.stop()

    def music_set_volume(self, volume):
        if 0 <= volume <= 1:
            self.music_volume = volume
            self.music.set_volume(volume)
        else:
            raise ValueError("Volume must be between 0 and 1")

    def notice_play(self, path):
        if self.current_notice and pygame.mixer.get_busy():
            self.current_notice.stop()

        self.fade_volume(self.music_volume * 0.3, 1)

        if self.play_notice_effect:
            self.notice_effect.play()
        
        while pygame.mixer.get_busy():
            time.sleep(0.1)
        
        self.current_notice = pygame.mixer.Sound(path)
        self.current_notice.set_volume(self.notice_volume)
        self.current_notice.play()
        
        while pygame.mixer.get_busy():
            time.sleep(0.1)
        
        self.fade_volume(self.music_volume, 1)

    def notice_stop(self):
        if self.current_notice:
            self.current_notice.stop()

    def notice_set_volume(self, volume):
        if 0 <= volume <= 1:
            self.notice_volume = volume
            self.notice_effect.set_volume(volume * 0.8)
            if self.current_notice:
                self.current_notice.set_volume(volume)
        else:
            raise ValueError("Volume must be between 0 and 1")
