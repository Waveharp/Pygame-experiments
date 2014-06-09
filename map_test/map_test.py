import pygame
import tilerender
from pygame.locals import *
from pytmx import tmxloader

pygame.init()

# the clock object makes sure program runs
# (at most) a certain FPS
fpsClock = pygame.time.Clock()

size = [640, 480]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Map Test")


def main():
	done = False

	clock = pygame.time.Clock()

	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True

				
	clock.tick(60)
	pygame.display.flip()

	pygame.quit()	

tmxdata = tmxloader.load_pygame("test.tmx")
image = tmxdata.get_tile_image(1, 1, 1)
screen.blit(image)

if __name__ == "__main__":
	main()