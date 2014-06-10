import pygame
import tilerender

class _State(object):
	"""
	Base class for all game states.
	"""
	def __init__(self):
		self.start_time = 0.0
		self.current_time = 0.0
		self.done = False
		self.quit = False
		self.next = None
		self.previous = None
		self.game_data = {}

	def get_event(self, event):
		pass

	def startup(self, current_time, game_data):
		self.game_data = game_data
		self.start_time = current_time
		self.renderer = tilerender.Renderer(self.tmx_map)
		self.map_image = self.renderer.make_map()

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

	def make_blockers(self, blocker_name):
		"""
		Make collideable blockers the player can collide with. 
		"""
		blockers = pygame.sprite.Group()
		for object in self.renderer.tmx_data.getObjects():
			properties = object.__dict__
			if properties['name'] == blocker_name:
				x = properties['x']
				y = properties['y'] - 70
				width = height = 70