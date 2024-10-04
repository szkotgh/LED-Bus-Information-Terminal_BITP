import pygame
import time
import os

# Initialize pygame mixer
pygame.mixer.init()

# Load music and notice
music_path = "/home/bituser/BITP/src/audio/music1.mp3"
music_path = "/home/bituser/BITP/src/audio/悪魔の子.mp3"
notice_ef_path = "/home/bituser/BITP/src/audio/notice_effect.mp3"
notice_path = "/home/bituser/BITP/src/audio/notice_1.mp3"
notice_path2 = "/home/bituser/BITP/src/audio/notice.mp3"

# Set initial volume levels
music_volume = 1
notice_volume = 1
notice_effect = True

# Load and play music
pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(music_volume)
pygame.mixer.music.play(-1)  # Play music on loop

# Function to play notice and adjust volume
def play_notice(notice_path, music_volume, notice_volume, fade_duration=1):
    def fade_volume(target_volume, duration, steps=20):
        current_volume = pygame.mixer.music.get_volume()
        step_size = (target_volume - current_volume) / steps
        for _ in range(steps):
            current_volume += step_size
            pygame.mixer.music.set_volume(current_volume)
            time.sleep(duration / steps)
    
    # Fade out the volume of the music
    fade_volume(music_volume * 0.3, fade_duration)
    
    if notice_effect:
        # Load and play the notice effect sound
        notice = pygame.mixer.Sound(notice_ef_path)
        notice.set_volume(notice_volume * 0.8)
        notice.play()
        
        # Wait for the notice to finish
        while pygame.mixer.get_busy():
            time.sleep(0.1)
    
    notice = pygame.mixer.Sound(notice_path)
    notice.set_volume(notice_volume)
    notice.play()

    # Wait for the notice to finish
    while pygame.mixer.get_busy():
        time.sleep(0.1)

    # Fade in the volume of the music
    fade_volume(music_volume, fade_duration)

# Main function to demonstrate
if __name__ == "__main__":
    try:
        while True:
            # Simulate some waiting time before playing notice
            time.sleep(5)
            # play_notice(notice_path2, music_volume, notice_volume)
            # play_notice(notice_path, music_volume, notice_volume)
    except KeyboardInterrupt:
        # Stop the music when the program is interrupted
        pygame.mixer.music.stop()
        print("\nProgram terminated.")
