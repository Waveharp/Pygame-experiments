import pygame
from pygame.locals import *

from xml import sax

from maputils import TMXHandler
from maputils import Tileset

import sys

def main():
    if(len(sys.argv)!=2):
        print 'Usage:\n\t{0} filename'.format(sys.argv[0])
        sys.exit(2)
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    parser = sax.make_parser()
    tmxhandler = TMXHandler()
    parser.setContentHandler(tmxhandler)
    parser.parse(sys.argv[1])
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
        screen.fill((255,255,255))
        screen.blit(tmxhandler.image, (0,0))
        pygame.display.flip()
        pygame.time.delay(1000/60)

if __name__ == "__main__": main()
