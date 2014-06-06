# -*- coding: utf-8; -*-

import logging
from pubsub import pub
import pygame.display
import pygame.font
import pygame.draw
logger = logging.getLogger("platakart.title")

from platakart.ui import Scene


class ControllerConfScene(Scene):

    def __init__(self):
        self.options = None
        self.reloadable = True

    def get_name(self):
        return "controller-conf"

    def setup(self, options):
        self.options = options
        logger.debug("Setting up controller conf scene")
        pass

    def teardown(self):
        logger.debug("Tearing down controller conf scene")

    def update(self, delta):
        pass

    def draw(self, screen, rect):
        pass
