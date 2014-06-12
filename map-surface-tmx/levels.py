import pygame as pg 
import levels
import tilerender
import constants
import main
from spritesheet_functions import SpriteSheet 

class Level(object):
	""" Generic super-class for levels. """
	platform_list = None
	background = None

	def __init__(self, name):
		self.name = name
		self.tmx_map = main.tmx_file
		self.platform_list = pg.sprite.Group()
		self.player = player

	def draw(self, screen):
		self.fill(constants.BLACK)
		screen.blit(self.background)

	def make_blockers(self, blocker_name):
		"""
		Make collideable blockers.
		"""
		pass

class Level_01(Level):
	def __init__(self, name):
		Level.__init__(self, name)
		tmx_file = os.path.join(os.getcwd(), name)