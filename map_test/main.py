import pygame, sys
import constants
import tilerender
import level
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

windowSurfaceObj = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Map Test, Python 2')

mousex, mousey = 0, 0

while True:
	windowSurfaceObj.fill(constants.WHITE)

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()


	pygame.display.update()
	fpsClock.tick(30)