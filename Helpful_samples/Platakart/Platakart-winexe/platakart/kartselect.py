# -*- coding: utf-8; -*-

import logging
from pubsub import pub
import pygame.display
import pygame.font
import pygame.sprite

logger = logging.getLogger("platakart.kartselect")

from platakart.ui import labeled_button
from platakart.ui import BLACK
from platakart.ui import Scene
from platakart.ui import Menu

FADE_COLOR = BLACK


class KartSelectScene(Scene):
    def __init__(self, resources):
        Scene.__init__(self)
        self.resources = resources
        self.selected_kart_id = None
        self.background = None
        self.menu = None
        self.rect = None
        self.options = None

    def get_name(self):
        return "kart-select"

    def setup(self, options):
        logger.debug("Setting up kart select scene")
        pub.subscribe(self.on_button_clicked, "button.clicked")
        self.font = pygame.font.SysFont("Verdana", 32)
        self.options = options

    def teardown(self):
        logger.debug("Tearing down kart select scene")
        pub.unsubscribe(self.on_button_clicked, "button.clicked")
        self.font = None
        self.menu.teardown()

    def build_menu(self, surface, rect):
        self.menu = Menu(rect)
        self.menu.setup()

        for index, kart_id in enumerate(self.resources.karts):
            record = self.resources.karts[kart_id]
            image = self.resources.images[record.select_thumb]
            label = record.name

            # TODO: better positioning
            x = rect.width * .66
            y = index * 64 + rect.height * .2
            button = labeled_button(kart_id, label, self.font, (x, y),
                                    self.resources.images["red_button_up"],
                                    self.resources.images["red_button_down"],
                                    self.resources.images["red_button_focus"])

            # INFO: this sprite is built b/c it may be scrolled ...later...
            static = pygame.sprite.Sprite()
            static.image = image
            static.rect = image.get_rect().move((rect.width * .1, y))

            # TODO: should menu have static elements?  ie: not selectable?
            #self.menu.add(static)
            surface.blit(static.image, static.rect)

            self.menu.add(button)

    def draw(self, surface, rect):
        dirty = list()

        if self.background is None:
            self.background = pygame.Surface(rect.size)
            image = self.resources.images["kart-select"]
            pygame.transform.scale(image, rect.size, self.background)
            surface.blit(self.background, (0,0))
            pub.sendMessage("game.play-sound", name="kart-select", loops=-1)
            dirty.append(rect)

        if self.rect is not rect:
            self.rect = rect
            self.build_menu(surface, rect)

        self.menu.clear(surface, self.background)
        dirty.extend(self.menu.draw(surface))

        return dirty

    def on_button_clicked(self, id):
        logger.debug("Kart {%s} selected" % id)
        self.selected_kart_id = id

        # id for the player
        player = 1

        # setup player_karts
        player_karts = {self.resources.karts[id].id: player}

        # setup npc karts
        npc_karts = ["atma-weapon"]

        # setup all karts
        all_karts = player_karts.keys()
        all_karts.extend(npc_karts)

        self.options["player-karts"] = player_karts
        self.options["karts"] = all_karts

        pub.sendMessage("game.switch-scene",
                        name="track-select",
                        options=self.options)

