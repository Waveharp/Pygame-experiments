"""
Global constants
"""
import pygame as pg 

# colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
RED = (255,0,0)
GREEN = (0,255,0)
SPRITESHEET_BACKGROUND = (94, 129, 162)

CAPTION = "Moving Platforms"
SCREEN_SIZE = (700,500)

# player directions
DIRECT_DICT = {pg.K_LEFT : (-1, 0),
				pg.K_RIGHT : (1, 0),
				pg.K_UP : (0, -1),
				pg.K_DOWN : (0, 1)}