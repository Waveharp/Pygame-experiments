import pygame as pg 
import constants as c
from spritesheet_functions import SpriteSheet

"""
The Player class will be a player-controlled sprite
that will collide with the blockers we just created.
We pass in the blockers as a constructor argument so 
that we can assign them as an attribute.  During the 
update method, we can refer to this attribute to detect
collision.
"""

class Player(pg.sprite.Sprite):
	# attributes for making the player sprite
	initial_r = []
	initial_l = []
	walking_frames_r = []
	walking_frames_l = []
	direction = "R"
	size = 0
	factor = 2

	def __init__(self, blockers):
		super(Player, self).__init__()
		# sprite processing, probably need to move this
		# to a separate module
		
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
			image.set_colorkey(c.SPRITESHEET_BACKGROUND)
			size = image.get_size()
			bigger_img = pg.transform.scale(image, (int(size[0]*self.factor),
														int(size[1]*self.factor)))
			self.walking_frames_r.append(bigger_img)

		for image in self.initial_l:
			image.set_colorkey(c.SPRITESHEET_BACKGROUND)
			size = image.get_size()
			bigger_img = pg.transform.scale(image, (int(size[0]*self.factor),
														int(size[1]*self.factor)))
			self.walking_frames_l.append(bigger_img)

		# set starting player image
		self.image = self.walking_frames_r[0]

		# set reference to image rect
		# obiously don't need both of these
		self.rect = self.image.get_rect()
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
		self.calc_grav()
		pos = self.rect.x
		# Animates sprite as you walk
		if self.direction == "R":
			frame = (pos // 30) % len(self.walking_frames_r)
			self.image = self.walking_frames_r[frame]
		else:
			frame = (pos // 30) % len(self.walking_frames_l)
			self.image = self.walking_frames_l[frame]

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

	def calc_grav(self):
		if self.y_vel == 0:
			self.y_vel = 1
		else:
			self.y_vel += .5

		if self.rect.y >= c.SCREEN_HEIGHT - self.rect.height and self.y_vel >= 0:
			self.y_vel = 0
			self.rect.y = c.SCREEN_HEIGHT - self.rect.height


	def jump(self):
		self.y_vel = -6

	def go_left(self):
		self.x_vel = -6
		self.direction = "L"

	def go_right(self):
		self.x_vel = 6
		self.direction = "R"

	def stop(self):
		self.x_vel = 0