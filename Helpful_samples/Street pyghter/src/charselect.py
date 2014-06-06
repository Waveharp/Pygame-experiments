import pygame, os
import config
import menu
from menu import getCharList
from Round import Player
from game import *
    

if __name__ == "__main__":    
    print('loading...')
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((320, 240), 0, 32)
    pygame.display.set_caption("charSelect") # program title
    
    config = config.OptionConfig()
    print('Loading all...')
    for name in getCharList():
        print('loading', name+'...')
        char = Player(name, 120, 100, alt_color = False)
        altchar = Player(name, 120, 100, alt_color = True)
        print(name, 'ok')
    menu = menu.CharSelectMenu(screen, config.keysP1, config.keysP2, Point(0,0))
    menu.mainloop()
    