import pygame as pg 
import constants as c 
import os, tilerender

class Level(object):
	def __init__(self):
		self.tmx_file = os.path.join(os.getcwd(), 'test.tmx')
		self.tile_renderer = tilerender.Renderer(self.tmx_file)
		self.map_surface = self.tile_renderer.make_map()
		self.map_rect = self.map_surface.get_rect()


	def make_blockers(self):
		pass