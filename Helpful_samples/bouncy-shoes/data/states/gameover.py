"""
Main menu state
"""
import pygame as pg
from .. import tools, setup
from .. import constants as c
from ..sprites import player

class GameOver(tools._State):
    def __init__(self):
        super(GameOver, self).__init__()

    def startup(self, current_time, game_data):
        self.game_data = game_data
        self.next = c.MAIN_MENU
        self.level_rect = setup.SCREEN.get_rect()
        text = 'GAME OVER'
        self.font = pg.font.Font(setup.FONTS['alienleague'], 60)
        self.rendered_text = self.font.render(text, 1, c.WHITE)
        location = self.level_rect.centerx, self.level_rect.y+150
        self.text_rect = self.rendered_text.get_rect(center=location)
        self.name = c.MAIN_MENU
        self.background = setup.GFX['spacebackground2']
        self.background_rect = self.background.get_rect(bottom=self.level_rect.bottom)
        self.player = player.Player(50, 400, self)
        self.player.state = c.AUTOWALK
        self.allow_input = False
        self.timer = current_time

    def update(self, surface, keys, current_time, dt):
        self.current_time = current_time
        self.player.update(keys, current_time, dt)
        surface.blit(self.background, self.background_rect)
        surface.blit(self.rendered_text, self.text_rect)
        surface.blit(self.player.image, self.player.rect)

    def get_event(self, event):

        if (self.current_time - self.timer) > 2000:
            if event.type == pg.KEYUP:
                self.game_data['last state'] = self.name
                self.done = True
                pg.mixer.music.stop()

