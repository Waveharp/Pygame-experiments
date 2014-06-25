import os, sys
from random import randint, choice
from math import sin, cos, radians

from pygame.sprite import Sprite
import pygame as pg 
#from pygame.sprite import Sprite

from vec2d import vec2d


BG_COLOR = 150, 150, 80
CREEP_FILENAMES = [
	'bluecreep.png',
	'pinkcreep.png',
	'graycreep.png']
N_CREEPS = 150
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400

screen = pg.display.set_mode(
		(SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
creeps = []

class Creep(Sprite):
	""" A creep sprite that bounces off walls and changes its
	direction from time to time. """
	def __init__(self, screen, img_filename, init_position,
				init_direction, speed):
		"""Create a new Creep.
			init_position: A vec2d or a pair specifying the initial
			position of the creep on the screen. """

		Sprite.__init__(self)

		self.screen = screen
		self.speed = speed

		self.base_image = pg.image.load(img_filename).convert_alpha()
		self.image = self.base_image

		self.pos = vec2d(init_position)

		self.direction = vec2d(init_direction).normalized()

	def update(self, time_passed):
		# time to change direction?
		self._change_direction(time_passed)

		# make creep point in the correct direction.
		self.image = pg.transform.rotate(
			self.base_image, -self.direction.angle)

		# Compute and apply displacement to the position
		# vector. Displacement is a vector, having the angle
		# of self.direction (which is normalized to not affect
		# the magnitude of the displacement).
	
		displacement = vec2d(
			self.direction.x * self.speed * time_passed,
			self.direction.y * self.speed * time_passed)

		self.pos += displacement

		self.image_w, self.image_h = self.image.get_size()
		bounds_rect = self.screen.get_rect().inflate(
			-self.image_w, -self.image_h)

		if self.pos.x < bounds_rect.left:
			self.pos.x = bounds_rect.left
			self.direction.x *= -1
		elif self.pos.x > bounds_rect.right:
			self.pos.x = bounds_rect.right
			self.direction.x *= -1
		elif self.pos.y < bounds_rect.top:
			self.pos.y = bounds_rect.top
			self.direction.y *= -1
		elif self.pos.y > bounds_rect.bottom:
			self.pos.y = bounds_rect.bottom
			self.direction.y *= -1

	def blitme(self):
		""" BLit the creep onto the screen that was provided in constructor."""
		# creep image is placed at self.pos.
		# To allow for smooth movement even when creep rotates
		# and image size changes, its placement is always centered.
		draw_pos = self.image.get_rect().move(
			self.pos.x - self.image_w / 2,
			self.pos.y - self.image_h / 2)
		self.screen.blit(self.image, draw_pos)

	_counter = 0

	def _change_direction(self, time_passed):
		self._counter += time_passed
		if self._counter > randint(300, 400):
			self.direction.rotate(45 * randint(-1, 1))
			self._counter = 0

def run_game():
	pg.init()
	clock = pg.time.Clock()

	#create N_CREEPS random creeps
	make_creeps()

	while True:
		time_passed = clock.tick(50)

		for event in pg.event.get():
			if event.type == pg.QUIT:
				exit_game()

		screen.fill(BG_COLOR)

		for creep in creeps:
			creep.update(time_passed)
			creep.blitme()

		pg.display.flip()

def make_creeps():
	for i in range(N_CREEPS):
		creeps.append(Creep(screen,
						choice(CREEP_FILENAMES),
							(randint(0, SCREEN_WIDTH),
							randint(0, SCREEN_HEIGHT)),
							(choice([-1, 1]),
							choice([-1, 1])),
							0.1))
	return creeps

def exit_game():
	sys.exit()

run_game()