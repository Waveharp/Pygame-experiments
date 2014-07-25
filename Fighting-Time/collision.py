"""
Handle game collisions.
"""
import tools
import pygame as pg
import constants as c

class CollisionHandler(object):
	"""
	Handles collisions between the player and game objects.
	"""
	def __init__(self, player, sprites, blockers, level):
		self.player = player
		self.sprites = sprites
		self.blockers = blockers
		self.level = level

	def make_state_dict(self):
		"""
		Make dictionary for collision handler states.
		"""
		state_dict = {c.WALKING: self.update_walking_player,
					  c.FREE_FALL: self.update_player_in_freefall,
					  c.STANDING: self.update_walking_player}

		return state_dict

	def update(self, keys):
		state_function = self.state_dict[self.player.state]
		state_function(keys)

	def update_walking_player(self, keys):
		"""
		Move player when walking.
		"""
		self.adjust_horizontal_motion(keys)
		self.player.rect.x += self.player.x_vel

		if self.player.x_vel > 0:
			if self.player.x_vel <= 25.0:
				self.player.enter_standing()
		else:
			if self.player.x_vel >= -25.0:
				self.player.enter_standing()

	