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


class CircuitSelectScene(Scene):
    def __init__(self, resources):
        Scene.__init__(self)
        self.resources = resources
        self.selected_circuit_id = None
        self.background = None
        self.menu = None
        self.rect = None
        self.options = None
        self.reloadable = True

    def get_name(self):
        return "circuit-select"

    def setup(self, options):
        logger.debug("Setting up circuit select scene")
        pub.subscribe(self.on_button_clicked, "button.clicked")
        self.font = pygame.font.SysFont("Verdana", 32)
        self.options = options

    def teardown(self):
        logger.debug("Tearing down circuit select scene")
        pub.unsubscribe(self.on_button_clicked, "button.clicked")
        self.font = None
        self.menu.teardown()

    def build_menu(self, surface, rect):
        self.menu = Menu(rect)
        self.menu.setup()

        for index, circuit_id in enumerate(self.resources.circuits):
            record = self.resources.circuits[circuit_id]
            image = self.resources.images[record.thumbnail]
            label = record.name

            # TODO: better positioning
            x = rect.width * .66
            y = index * 64 + rect.height * .2
            button = labeled_button(circuit_id, label, self.font, (x, y),
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
            image = self.resources.images["circuit-select"]
            pygame.transform.scale(image, rect.size, self.background)
            surface.blit(self.background, (0, 0))
            pub.sendMessage("game.play-sound", name="circuit-select", loops=-1)
            dirty.append(rect)

        if self.rect is not rect:
            self.rect = rect
            self.build_menu(surface, rect)

        self.menu.clear(surface, self.background)
        dirty.extend(self.menu.draw(surface))

        return dirty

    def on_button_clicked(self, id):
        logger.debug("Circuit {%s} selected" % id)

        self.options["circuit-id"] = id

        #pub.sendMessage("game.switch-scene",
        #                name="track-select",
        #                options=self.options)

