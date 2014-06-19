import pygame as pg 
import constants as c 
from spritesheet_functions import SpriteSheet 


class Player(pg.sprite.Sprite):
	def __init__(self, x, y, level):
		super(Player, self).__init__()
		self.get_image = SpriteSheet.get_image
		self.state = c.STANDING
		self.walking_image_dict = self.make_walking_image_dict()
		self.standing_image_dict = self.make_standing_image_dict()
		self.jumping_image_dict = self.make_jumping_image_dict()
		self.index = 0
		self.timer = 0.0
		self.direction = c.RIGHT
		self.x_vel = 0
		self.y_vel = 0
		self.max_speed = c.WALK_SPEED
		self.allow_jump = False
		self.image = self.standing_image_dict[self.direction]
		self.rect = self.image.get_rect(x=x, bottom=y)
		self.level_bottom = level.level_rect.bottom

	def make_state_dict(self):
		state_dict = {c.STANDING: self.standing,
						c.WALKING: self.walking,
						c.FREE_FALL: self.free_fall}
		return state_dict

	def standing(self, keys, current_time, dt):
		self.image = self.standing_image_dict[self.direction]

		if keys[pg.K_RIGHT]:
			self.index = 0
			self.direction = c.RIGHT
			self.state = c.WALKING
			self.timer = current_time
		elif keys[pg.K_LEFT]:
			self.index = 0
			self.direction = c.LEFT
			self.state = c.WALKING
			self.timer = current_time
		if keys[c.JUMP_BUTTON] and self.allow_jump:
			self.enter_jump()

		if not keys[c.JUMP_BUTTON]:
			self.allow_jump = True

	def walking(self, keys, current_time, dt):
		self.image_list = self.walking_image_dict[self.direction]
		self.image = self.image_list[self.index]
		self.animate(current_time, dt)

		if keys[pg.K_RIGHT]:
			self.direction = c.RIGHT
		elif keys[pg.K_LEFT]:
			self.direction = c.LEFT
		if keys[c.JUMP_BUTTON] and self.allow_jump:
			self.enter_jump()
		if keys[c.RUN_BUTTON]:
			self.max_speed = c.RUN_SPEED
		elif not keys[c.RUN_BUTTON]:
			self.max_speed = c.WALK_SPEED

		if not keys[c.JUMP_BUTTON]:
			self.allow_jump = True

	def animate(self, current_time, dt):
		if (current_time - self.timer) > self.get_animation_speed(dt):
			self.timer = current_time
			if self.index < (len(self.image_list) - 1):
				self.index += 1
			else:
				self.index = 0

	def get_animation_speed(self, dt):
		if self.x_vel == 0:
			frequency = c.SLOWEST_FREQUENCY
		elif self.x_vel > 0:
			frequency = c.SLOWEST_FREQUENCY - (self.x_vel * 11 * dt)
		else:
			frequency = c.SLOWEST_FREQUENCY - (self.x_vel * dt * 11 * -1)

		return frequency

	def enter_jump(self):
		self.state = c.FREE_FALL
		self.y_vel = c.START_JUMP_VEL

	def free_fall(self, keys, *args):
		self.image = self.jumping_image_dict[self.direction]
		if keys[pg.K_RIGHT]:
			self.direction = c.RIGHT
		elif keys[pg.K_LEFT]:
			self.direction = c.LEFT

	def make_walking_image_list(self, sprite_sheet, reverse_images=False):
		coord = []
		for y in range(2):
			for x in range(6):
				coord.append((x, y))

		walking_images = []
		for pos in coord:
			width = 17
			height = 21
			x = pos[0] * width
			y = pos[1] * height
			walking_images.append(self.get_image(x, y,
												width, height,
												sprite_sheet))
		walking_images.pop(-1)

		if reverse_images:
			flipped_images = []
			for image in walking_images:
				flipped_images.append(pg.transform.flip(image, True, False))
			return flipped_images
		else:
			return walking_images

	def make_standing_image_dict(self):
		sheet = SpriteSheet('spritesheet.png')
		right_image = self.get_image(441, 2, 17, 21, sheet)
		left_image = pg.transform.flip(right_image, True, False)

		return {c.RIGHT: right_image,
				c.LEFT: left_image}

	def make_jumping_image_dict(self):
		sheet = SpriteSheet('spritesheet.png')
		right_image = self.get_image(486, 2, 17, 21, sheet)
		left_image = pg.transform.flip(right_image, True, False)

		return {c.RIGHT: right_image, 
				c.LEFT: left_image}

	def update(self, keys, current_time, dt):
		state_function = self.state_dict[self.state]
		state_function(keys, current_time, dt)

	def enter_walking(self):
		self.allow_jump = False
		self.y_vel = 0
		self.state = c.WALKING

	def enter_standing(self):
		self.state = c.STANDING
		self.x_vel = 0

	def enter_fall(self):
		self.state = c.FREE_FALL
		self.y_vel = 0