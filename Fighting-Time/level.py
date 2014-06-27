import pygame as pg 
import constants as c 
import os, tilerender

class Level(object):
	def __init__(self):
		self.tmx_file = os.path.join(os.getcwd(), 'test.tmx')
		self.tile_renderer = tilerender.Renderer(self.tmx_file)
		self.map_surface = self.tile_renderer.make_map()
		self.map_rect = self.map_surface.get_rect()

		self.blockers = self.make_blockers('blocker')

	def make_blockers(self, blocker_name):
		blockers = []
		for object in self.tile_renderer.tmx_data.getObjects():
			properties = object.__dict__
			if properties['name'] == blocker_name:
				x = properties['x']
				y = properties['y']
				width = properties['width']
				height = properties['height']
				new_rect = pg.Rect(x, y, width, height)
				blockers.append(new_rect)
		return blockers