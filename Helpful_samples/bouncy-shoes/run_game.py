"""
This is a side-scrolling platformer about a character
who can wear shoes that make him bounce really high.
"""

import sys
import pygame as pg
from data import setup
from data.main import main

if __name__=='__main__':
    setup.GAME
    main()
    pg.quit()
    sys.exit()