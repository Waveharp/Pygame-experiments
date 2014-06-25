import pygame as pg 
import constants as c 


class Control(object):
	def __init__(self):
		self.screen = pg.display.get_surface()
		self.clock = pg.time.Clock()
		self.fps = 60.0
		self.keys = pg.key.get_pressed()
		self.done = False

	def event_loop(self):
		self.events = pg.event.get()

		for event in self.events:
			if event.type == pg.QUIT:
				self.done = True
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					self.done = True
				self.keys = pg.key.get_pressed()
			elif event.type == pg.KEYUP:
				self.keys = pg.key.get_pressed()

	def main_loop(self):
		while not self.done:
			self.event_loop()
			self.update()
			self.draw()
			pg.display.update()
			self.clock.tick(self.fps)
			self.display_fps()