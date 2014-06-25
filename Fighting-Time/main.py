import os, tools
import pygame as pg 
import constants as c 


if __name__ == "__main__":
    os.environ['SDLE_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(c.CAPTION)
    pg.display.set_mode(c.SCREEN_SIZE)
    run_it = tools.Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()