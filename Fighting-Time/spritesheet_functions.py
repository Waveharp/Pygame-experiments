"""
Used to pull individual sprites from the sprite sheets.
"""

import pygame
import constants

class SpriteSheet(object):
	"""Grabs images out of sprite sheet."""
	# points to the sprite sheet image
	sprite_sheet = None

	def __init__(self, file_name):
		"""Constructor. Pass in file name of sprite sheet."""
		# load the sheet
		self.sprite_sheet = pygame.image.load(file_name).convert()

	def get_image(self, x, y, width, height):
		""" Grab a single image, pass in x, y location
		and width and height of sprite. """

		# create a new, blank image
		image = pygame.Surface([width, height]).convert()

		# copy sprite from large sheet onto smaller image
		image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))

		# assuming black works as the transparent color
		image.set_colorkey(constants.BLACK)

		return image