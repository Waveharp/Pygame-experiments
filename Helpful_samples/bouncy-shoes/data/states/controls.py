"""
Main menu state
"""
import pygame as pg
from .. import tools, setup
from .. import constants as c
from ..sprites import player

class Controls(tools._State):
    def __init__(self):
        super(Controls, self).__init__()

    def startup(self, current_time, game_data):
        self.game_data = game_data
        self.next = c.LEVEL1
        self.level_rect = setup.SCREEN.get_rect()
        text = 'Arrows for direction, a for jump, s for run'
        text2 = 'Help 8-bit the Alien find his way to the magic door!'
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.rendered_text = self.font.render(text, 1, c.WHITE)
        self.rendered_text2 = self.font.render(text2, 1, c.WHITE)
        location = self.level_rect.centerx, self.level_rect.y+150
        location2 = self.level_rect.centerx, self.level_rect.y+250
        self.text_rect = self.rendered_text.get_rect(center=location)
        self.text_rect2 = self.rendered_text2.get_rect(center=location2)
        self.name = c.MAIN_MENU
        self.background = setup.GFX['spacebackground2']
        self.background_rect = self.background.get_rect(bottom=self.level_rect.bottom)
        self.player = player.Player(50, 400, self)
        self.player.state = c.AUTOWALK

    def update(self, surface, keys, current_time, dt):
        self.current_time = current_time
        self.player.update(keys, current_time, dt)
        surface.blit(self.background, self.background_rect)
        surface.blit(self.rendered_text, self.text_rect)
        surface.blit(self.rendered_text2, self.text_rect2)
        surface.blit(self.player.image, self.player.rect)

    def get_event(self, event):
        if event.type == pg.KEYUP:
            self.game_data['last state'] = self.name
            self.done = True
            pg.mixer.music.stop()
