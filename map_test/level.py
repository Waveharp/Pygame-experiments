import pygame
import tilerender
import constants

class _State(object):
	def __init__(self):
		self.start_time = 0.0
		self.current_time = 0.0
		self.done = False
		self.quit = False
		self.next = None
		self.previous = None
		self.game_data = {}

	def  get_event(self, event):
		pass

	def startup(self, current_time, game_data):
		self.game_data = game_data
		self.start_time = current_time

	def cleanup(self):
		self.done = False
		return self.game_data

	def update(self, surface, keys, current_time, dt):
		pass

class Level(_State):
	def __init__(self, name):
		super(Level, self).__init__()
		self.name = name
		self.tmx_map = setup.TMX[name]

	def startup(self, current_time, game_data):
		self.game_data = game_data
		self.current_time = current_time
		self.renderer = tilerender.Renderer(self.tmx_map)
		self.map_image = self.renderer.make_map()

		self.viewport = self.make_viewport(self.map_image)
		self.level_surface = self.make_level_surface(self.map_image)
		self.level_rect = self.level_surface.get_rect()
		