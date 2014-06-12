import pygame as pg 
import constants as c

"""
The Player class will be a player-controlled sprite
that will collide with the blockers we just created.
We pass in the blockers as a constructor argument so 
that we can assign them as an attribute.  During the 
update method, we can refer to this attribute to detect
collision.
"""

class Player(pg.sprite.Sprite):
	def __init__(self, blockers):
		super(Player, self).__init__()
		self.image = pg.Surface((22, 22))
		self.image.fill((130, 100, 200))
		self.rect = self.image.get_rect(x = 100, y = 100)
		self.x_vel = 0
		self.y_vel = 0
		self.blockers = blockers

	def update(self, keys):
		"""
		Set player velocity by keys, move by vel, check
		for collision. It's important to check collisions
		for both on the x-axis and y-axis, rather than just once.
		"""
		if keys[pg.K_DOWN]:
			self.y_vel = 3
		elif keys[pg.K_UP]:
			self.y_vel = -3
		else:
			self.y_vel = 0
		if keys[pg.K_LEFT]:
			self.x_vel = -3
		elif keys[pg.K_RIGHT]:
			self.x_vel = 3
		else:
			self.x_vel = 0

		self.rect.x += self.x_vel
		for blocker in self.blockers:
			if self.rect.colliderect(blocker):
				self.rect.x -= self.x_vel
				self.x_vel = 0

		self.rect.y += self.y_vel
		for blocker in self.blockers:
			if self.rect.colliderect(blocker):
				self.rect.y -= self.y_vel
				self.y_vel = 0

	def draw(self, surface):
		"""
		Blit player image to screen.
		"""
		surface.blit(self.image, self.rect)