import pygame

pygame.mixer.init()

pygame.mixer.music.load("/usr/local/LED-Bus-Information-Terminal_BITP/src/audio/music2.mp3")

pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(1000)