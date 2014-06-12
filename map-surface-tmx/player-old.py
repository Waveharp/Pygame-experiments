import pygame as pg
import constants as c 
from spritesheet_functions import *

class Player(pg.sprite.Sprite):
	change_x, change_y = 0, 0

	initial_r = []
	initial_l = []
	walking_frames_l = []
	walking_frames_r = []

	# what direction is player facing?
	direction = "R"

	# list of sprites we can bump
	level = None

	# stuff for enlarging sprite:
	size = 0
	factor = 3

	# -- Methods
	def __init__(self):
		pg.sprite.Sprite.__init__(self)
		sprite_sheet = SpriteSheet("spritesheet.png")
		# Load all right facing images into a list
		image = sprite_sheet.get_image(441, 2, 17, 21)
		self.initial_r.append(image)
		image = sprite_sheet.get_image(464, 2, 16, 21)
		self.initial_r.append(image)
		image = sprite_sheet.get_image(648, 2, 16, 21)
		self.initial_r.append(image)
		image = sprite_sheet.get_image(671, 2, 16, 21)
		self.initial_r.append(image)
		
		# Load all the right facing images, then flip them
		# to face left.
		for image in self.initial_r:
			image = pg.transform.flip(image, True, False)
			self.initial_l.append(image)

		for image in self.initial_r:
			image.set_colorkey(constants.SPRITESHEET_BACKGROUND)
			size = image.get_size()
			bigger_img = pg.transform.scale(image, (int(size[0]*self.factor),
														int(size[1]*self.factor)))
			self.walking_frames_r.append(bigger_img)

		for image in self.initial_l:
			image.set_colorkey(constants.SPRITESHEET_BACKGROUND)
			size = image.get_size()
			bigger_img = pg.transform.scale(image, (int(size[0]*self.factor),
														int(size[1]*self.factor)))
			self.walking_frames_l.append(bigger_img)

		# set starting player image
		self.image = self.walking_frames_r[0]

		# set reference to image rect
		self.rect = self.image.get_rect()

	def update(self):
		"""Move the player."""
		self.calc_grav()

		self.rect.x += self.change_x
		pos = self.rect.x
		if self.direction == "R":
			frame = (pos // 30) % len(self.walking_frames_r)
			self.image = self.walking_frames_r[frame]
		else:
			frame = (pos // 30) % len(self.walking_frames_l)
			self.image = self.walking_frames_l[frame]

		self.rect.y += self.change_y

	def calc_grav(self):
		if self.change_y == 0:
			self.change_y = 1
		else:
			self.change_y += .35

		if self.rect.y >= c.SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
			self.change_y = 0
			self.rect.y = c.SCREEN_HEIGHT - self.rect.height

	def jump(self):
		self.change_y = -6

	def go_left(self):
		self.change_x = -6
		self.direction = "L"

	def go_right(self):
		self.change_x = 6
		self.direction = "R"

	def stop(self):
		self.change_x = 0