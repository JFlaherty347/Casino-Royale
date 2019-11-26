import pygame

pygame.init()
pygame.mixer.music.load('bond.mp3')
pygame.mixer.music.play(1)
pygame.mixer.music.set_volume(0.4)

while pygame.mixer.music.get_busy():
	pygame.event.poll()
