import pygame
import time

music_paths = [
    "/home/admin/easy_lemon.wav",
]

count = 0;
for music_path in music_paths:
    count += 1
    
    #init
    pygame.mixer.init()

    #load file
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(100)

    #play
    print(f"playing music . . . '{music_path}' ({len(music_paths)}/{count})")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy() == True:
        time.sleep(1)
        continue

print("player dead")
    