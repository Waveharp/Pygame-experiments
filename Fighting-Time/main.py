import sys, os, tilerender, level
import pygame as pg 
import constants as c 

class Control(object):
	"""Class for managing event loop."""
	def __init__(self):
		"""Initialize display and prepare game objects."""
		self.screen = pg.display.get_surface()
		
		self.clock = pg.time.Clock()
		self.fps = 60.0
		self.keys = pg.key.get_pressed()
		self.done = False
		self.current_time = 0.0
		self.last_time = 0.0
		self.state_dict = {}
		self.state_name = None

	def setup_states(self, state_dict, start_state):
		self.state_dict = state_dict
		self.state_name = start_state
		self.state = self.state_dict[self.state_name]

	def update(self):
		self.last_time = self.current_time
		self.current_time = pg.time.get_ticks()
		self.delta_time = (self.current_time - self.last_time) / 1000

		self.state.update(self.screen, self.keys, self.current_time, self.delta_time)

	def flip_state(self):
		previous, self.state_name = self.state_name, self.state.next
		persist = self.state.cleanup()
		self.state = self.state_dict[self.state_name]
		self.state.startup(self.current_time, persist)
		self.state.previous = previous

	def event_loop(self):
		self.events = pg.event.get()
		for event in self.events:
			if event.type == pg.QUIT:
				self.done = True
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					self.done = True
				self.keys = pg.key.get_pressed()
				self.state.get_event(event)
			elif event.type == pg.KEYUP:
				self.keys = pg.key.get_pressed()
				self.state.get_event(event)

	def main(self):
		while not self.done:
			self.event_loop()
			self.update()
			pg.display.update()
			self.clock.tick(self.fps)

if __name__ == "__main__":
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pg.init()
	pg.display.set_caption(c.CAPTION)
	SCREEN = pg.display.set_mode(c.SCREEN_SIZE)
	SCREEN_RECT = SCREEN.get_rect()
	run_it = Control()
	state_dict = {c.LEVEL1: level.Level(c.LEVEL1)}
	run_it.setup_states(state_dict, c.LEVEL1)
	run_it.main()
	pg.quit()
	sys.exit()
