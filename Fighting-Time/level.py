import pygame as pg 
import constants as c 
import tilerender, player, os

class _State(object):
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
		self.start_time = start_time

	def cleanup(self):
		self.done = False
		return self.game_data

	def update(self, surface, keys, current_time, dt):
		pass

class Level(_State):
	def __init__(self, name):
		self.name = name
		self.tmx_map = os.path.join(os.getcwd(), name)

	def startup(self, current_time, game_data):
		self.game_data = game_data
		self.current_time = current_time
		self.state = c.NORMAL
		self.renderer = tilerender.Renderer(self.tmx_map)
		self.map_image = self.renderer.make_map()
		self.viewport = self.make_viewport(self.map_image)
		self.level_surface = self.make_level_surface(self.map_image)
		self.level_rect = self.level_surface.get_rect()
		self.player = self.make_player()
		# enemies
		#self.sprites = self.make_sprites()
		self.blockers = self.make_blockers('blocker')
		# uncomment below when collision file is complete
		#self.collision_handler = collision.CollisionHandler(self.player,
															#self.blockers)
		self.state_dict = self.make_state_dict()
		
	def make_viewport(self, map_image):
		map_rect = map_image.get_rect()

	def make_level_surface(self, map_image):
		map_rect = map_image.get_rect()
		map_width = map_rect.width 
		map_height = map_rect.height 
		size = map_width, map_height
		return pg.Surface(size).convert()

	def make_player(self):
		for object in self.renderer.tmx_data.getObjects():
			properties = object.__dict__
			if properties['name'] == 'player start point':
				x = properties['x']
				y = properties['y']
				return player.Player(x, y, self)

	def make_sprites(self):
		sprite_group = pg.sprite.Group()
		for object in self.renderer.tmx_data.getObjects():
			properties = object.__dict__
			if properties['type'] == 'enemy':
				name = properties['name']
				x = properties['x']
				y = properties['y']
				sprite_group.add(enemies.Enemy(x, y, name))
		return sprite_group

	def make_blockers(self, blocker_name):
		blockers = pg.sprite.Group()
		for object in self.renderer.tmx_data.getObjects():
			properties = object.__dict__
			if properties['name'] == blocker_name:
				x = properties['x']
				y = properties['y']
				width = properties['width']
				height = properties['height']
				blocker = pg.sprite.Sprite()
				blocker.state = None
				blocker.rect = pg.Rect(x, y, width, height)
				blockers.add(blocker)

		return blockers

	def make_state_dict(self):
		state_dict = {'normal': self.normal_mode}
		return state_dict

	def normal_mode(self, surface, keys, current_time, dt):
		self.player.update(keys, current_time, dt)
		self.viewport_update(dt)
		self.draw_level(surface)

	def viewport_update(self, dt):
		self.viewport.center = self.player.rect.midbottom
		self.viewport.clamp_ip(self.level_rect)

	def draw_level(self, surface):
		"""Blit all images to screen."""
		self.level_surface.blit(self.map_image, self.viewport, self.viewport)
		self.level_surface.blit(self.player.image, self.player.rect)
		surface.blit(self.level_surface, (0, 0), self.viewport)

	def end_game(self):
		self.next = c.GAME_OVER
		self.done = True