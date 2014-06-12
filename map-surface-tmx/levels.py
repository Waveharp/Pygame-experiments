import pygame as pg 
import levels
import tilerender
import constants
from spritesheet_functions import SpriteSheet 

class Level(object):
	def __init__(self, screen):
		self.screen = screen
		self.renderer = tilerender.Renderer('test.tmx')
		self.map_image = self.renderer.make_map()
		self.viewport = self.make_viewport(self.map_image)
		self.level_surface = self.make_level_surface(self.map_image)

	def make_level_surface(self, map_image):
		map_rect = map_image.get_rect()
		map_width = map_rect.map_width
		map_height = map_rect.map_height
		size = map_width, map_height
		return pg.Surface(size).convert()

	def make_viewport(self, map_image):
		map_rect = map_image.get_rect()
		return self.screen.get_rect()

	def render(self, screen):
		self.level_surface.blit(self.map_image, self.viewport, self.viewport)
		screen.blit(self.level_surface, (0,0), self.viewport)
