"""
Used to pull sprites from sprite sheets.
"""

import pygame as pg
import constants as c

class SpriteSheet(object):
	"""Grabs images out of sprite sheet."""
	sprite_sheet = None

	def __init__(self, file_name):
		self.sprite_sheet = pg.image.load(file_name).convert()

	def get_image(self, x, y, width, height):
		image = pg.Surface([width, height]).convert()
		image.blit(self.sprite_sheet, (0,0), (x, y, width, height))
		image.set_colorkey(c.BLACK)

		return image