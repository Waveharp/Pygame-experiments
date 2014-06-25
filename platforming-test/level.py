import pygame as pg 
import constants as c 
import player, tilerender
import os

class Level(object):
	def __init__(self):
		self.tmx_map = os.path.join(os.getcwd(), 'test.tmx')
		self.renderer = tilerender.Renderer(self.tmx_map)
		self.map_image = self.renderer.make_map()
		self.level_surface = self.make_level_surface(self.map_image)
		self.level_rect = self.level_surface.get_rect()

	def make_level_surface(self, map_image):
		map_rect = map_image.get_rect()
		map_width = map_rect.width 
		map_height = map_rect.height 
		size = map_width, map_height

		return pg.Surface(size).convert()

	def draw_level(self, surface):
		self.level_surface.blit(self.map_image)

	def make_player(self):
		for object in self.renderer.tmx_data.getObjects():
			properties = object.__dict__
			if properties['name'] == 'player start point':
				x = properties['x']
				y = properties['y']
				return player.Player(x, y, self)

	def make_blockers(self, blocker_name):
		blockers = pg.sprite.Group()
		for object in self.renderer.tmx_data.getObjects():
			properties = object.__dict__
			if properties['name'] == blocker_name:
				x = properties['x']
				y = properties['y']
				width = height = 21
				blocker = pg.sprite.Sprite()
				blocker.rect = pg.Rect(x, y, width, height)
				blockers.add(blocker)
		return blockers

