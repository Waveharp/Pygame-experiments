"""
Main menu state
"""
import pygame as pg
from .. import tools, setup
from .. import constants as c
from ..sprites import player

class Menu(tools._State):
    def __init__(self):
        super(Menu, self).__init__()
        self.next = c.CONTROLS
        self.level_rect = setup.SCREEN.get_rect()
        text = 'BOUNCY SHOES'
        self.font = pg.font.Font(setup.FONTS['alienleague'], 100)
        self.rendered_text = self.font.render(text, 1, c.WHITE)
        location = self.level_rect.centerx, self.level_rect.y+150
        self.text_rect = self.rendered_text.get_rect(center=location)
        self.game_data = tools.create_game_data_dict()
        self.name = c.MAIN_MENU
        self.background = setup.GFX['spacebackground2']
        self.background_rect = self.background.get_rect(bottom=self.level_rect.bottom)
        self.player = player.Player(50, 400, self)
        self.player.state = c.AUTOWALK


    def update(self, surface, keys, current_time, dt):
        if not pg.mixer.music.get_busy():
            pg.mixer.music.load(setup.MUSIC['title_music'])
            pg.mixer.music.play()
        self.current_time = current_time
        self.player.update(keys, current_time, dt)
        surface.blit(self.background, self.background_rect)
        surface.blit(self.rendered_text, self.text_rect)
        surface.blit(self.player.image, self.player.rect)

    def get_event(self, event):
        if event.type == pg.KEYUP:
            self.game_data['last state'] = self.name
            self.done = True
