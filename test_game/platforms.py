"""
module for managing platforms.
"""
import pygame
from spritesheet_functions import SpriteSheet 

# these constants define our platform types:
# name of file
# x location
# y location
# width
# height

STONE_WALL = (48, 255, 21, 21)

class Platform(pygame.sprite.Sprite):
	""" Platform the user can jump on. """
	def __init__(self, sprite_sheet_data):
		pygame.sprite.Sprite.__init__(self)
		
		sprite_sheet = SpriteSheet("spritesheet.png")
		# grab image for this platform
		self.image = sprite_sheet.get_image(sprite_sheet_data[0],
			sprite_sheet_data[1],
			sprite_sheet_data[2],
			sprite_sheet_data[3])
		self.rect = self.image.get_rect()

class MovingPlatform(Platform):
	change_x = 0
	change_y = 0

	boundary_top = 0
	boundary_bottom = 0
	boundary_left = 0
	boundary_right = 0

	level = None
	player = None

	def update(self):
		""" moves the platform.
		shoves player if in the way.
		does NOT handle what happens if player
		is pushed into another object"""

		# move left/right 
		self.rect.x += self.change_x

		# check if it hit the player
		hit = pygame.sprite.collide_rect(self, self.player)
		if hit:
			if self.change_x < 0:
				self.player.rect.right = self.rect.left
			else:
				self.player.rect.left = self.rect.right 

		# move up/down
		self.rect.y += self.change_y

		hit = pygame.sprite.collide_rect(self, self.player)
		if hit:
			if self.change_y < 0:
				self.player.rect.bottom = self.rect.top 
			else:
				self.player.rect.top = self.rect.bottom 

		if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
			self.change_y *= -1

		cur_pos = self.rect.x - self.level.world_shift
		if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
			self.change_x *= -1