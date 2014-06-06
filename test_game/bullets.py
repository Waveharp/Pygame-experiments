import pygame
import random
import constants
import player
from spritesheet_functions import *

class Bullet(pygame.sprite.Sprite):
	""" This class represents the bullet. """
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		sprite_sheet = SpriteSheet("spritesheet.png")
		self.image = sprite_sheet.get_image(421, 99, 11, 11)
		self.image.set_colorkey(constants.SPRITESHEET_BACKGROUND)
		self.rect = self.image.get_rect()

	def update(self):
		""" Move the bullet. """
		if player.Player.direction == "R":
			self.rect.x += 3
		elif player.Player.direction == "L":
			self.rect.x -= 3