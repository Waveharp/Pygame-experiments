import sys, os, tilerender
import pygame as pg 
import constants as c 



if __name__ == "__main__":
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pg.init()
	pg.display.set_caption(c.CAPTION)
	pg.display.set_mode(c.SCREEN_SIZE)
	run_it = Control()
	run_it.main_loop()
	pg.quit()
	sys.exit()