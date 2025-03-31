import pygame

pygame.mixer.init()

pygame.mixer.music.load("/usr/local/LED-Bus-Information-Terminal_BITP/src/audio/test_music1.mp3")

pygame.mixer.music.set_volume(1)
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(1000)