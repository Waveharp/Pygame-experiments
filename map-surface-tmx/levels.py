import pygame as pg 
import levels
import tilerender
import constants
from spritesheet_functions import SpriteSheet 

class Level():
	""" Generic super-class for levels. """
	platform_list = None
	background = None

	def __init__(self):
		self.platform_list = pg.sprite.Group()

	def draw(self, screen):
		self.fill(constants.BLACK)
		screen.blit(self.background)

class Level_01(Level):
	def __init__(self):
		Level.__init__(self)
		sprite_sheet = SpriteSheet("backgrounds.png")