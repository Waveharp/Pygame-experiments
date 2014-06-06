# -*- coding: utf-8; -*-

import logging
from pubsub import pub
import pygame.display
import pygame.font
import pygame.draw

logger = logging.getLogger("platakart.title")

from platakart.ui import Scene
from platakart.ui import Menu
from platakart.ui import labeled_button
from platakart.ui import WHITE
from platakart.ui import BLACK

PERCENT_COLOR = WHITE
FADE_COLOR = BLACK


class TitleScene(Scene):
    def __init__(self, resources):
        super(TitleScene, self).__init__()
        self.started_loading_resources = False
        self.render_title = False
        self.render_percent = False
        self.render_button = False
        self.resources = resources
        self.loader_gen = None
        self.loaded = False
        self.percent_surf = None
        self.fading_out = -0.1
        self.start_button_id = None
        self.menu = None
        self.background = None
        self.rect = None
        self.loaded_percent = 0
        self.group = pygame.sprite.RenderUpdates()

    def get_name(self):
        return "title"

    def setup(self):
        logger.debug("Setting up title scene")
        self.font = pygame.font.SysFont("Verdana", 32)
        pub.subscribe(self.on_resource_loaded, "resources.loading")
        pub.subscribe(self.on_resources_loaded, "resources.loaded")
        pub.subscribe(self.on_button_clicked, "button.clicked")
        self.menu = Menu(None)

    def teardown(self):
        logger.debug("Tearing down title scene")
        self.percent_surf = None
        self.render_title = False
        self.render_percent = False
        pub.unsubscribe(self.on_resource_loaded, "resources.loading")
        pub.unsubscribe(self.on_resources_loaded, "resources.loaded")
        pub.unsubscribe(self.on_button_clicked, "button.clicked")
        self.menu.teardown()

    def on_resources_loaded(self):
        pub.sendMessage("game.play-sound", name="menu-theme", loops=-1)
        self.render_button = True

        # make the start button
        # work around this event being caught twice
        logger.debug("making start button")
        screen = pygame.display.get_surface()
        screen_rect = screen.get_rect()
        self.menu = Menu(screen_rect)
        self.menu.setup()
        button = labeled_button("start", "PLAY", self.font, (0, 0),
                                self.resources.images["red_button_up"],
                                self.resources.images["red_button_down"],
                                self.resources.images["red_button_focus"])
        button.rect.centerx = screen_rect.centerx
        button.rect.top = screen_rect.height * .75
        self.menu.add(button)
        self.start_button_id = button.id

        # force the screen to redraw so the loading bar is covered up.
        self.render_title = True

    def on_resource_loaded(self, percent, category, key):
        if category == "image" and key == "title":
            self.render_title = True
        else:
            self.loaded_percent = percent
            self.percent_surf = self.font.render(
                "Loading %d%%" % int(percent * 100), True, PERCENT_COLOR)
            self.render_percent = True

    def on_button_clicked(self, id):
        logger.debug("Mouse clicked button")
        if id == self.start_button_id:
            pub.sendMessage("game.stop-sound", name="menu-theme", fade_ms=100)
            self.fading_out = 0.0

    def update(self, delta):
        self.menu.update(delta)

        if not self.loaded:
            if self.loader_gen is None:
                self.loader_gen = self.resources.load()
            else:
                try:
                    self.loader_gen.next()
                except StopIteration:
                    self.loaded = True
                    self.render_percent = False

        if self.fading_out >= 100:
            pub.sendMessage("game.switch-scene",
                            name="kart-select",
                            options={})

    def draw(self, surface, rect):
        dirty = list()

        # detect a change in the screen size
        if self.rect is not rect:
            self.rect = rect

        if self.background:
            self.group.clear(surface, self.background)
            self.menu.clear(surface, self.background)

        if self.render_title:
            self.background = pygame.Surface(rect.size)
            image = self.resources.images["title"]
            pygame.transform.scale(image, rect.size, self.background)
            surface.blit(self.background, rect)
            dirty.append(rect)
            self.render_title = False

        if self.render_percent:
            w = rect.width / 2
            h = self.percent_surf.get_height()
            x = rect.centerx - (w // 2)
            y = rect.height * .75
            new_rect = surface.fill((0, 0, 0), (x, y, w, h))
            surface.fill((255, 24, 24), (x, y, w * self.loaded_percent, h))
            surface.blit(self.percent_surf, (x + 4, y))
            dirty.append(new_rect)
            self.render_percent = False

        if 0 <= self.fading_out < 100:
            self.fading_out += 10
            fade_rect = surface.get_rect()
            amt = fade_rect.height * float(self.fading_out) / 100.0
            fade_rect.height = int(amt)
            pygame.draw.rect(surface, FADE_COLOR, fade_rect)
            dirty.append(fade_rect)

        dirty.extend(self.menu.draw(surface))

        return dirty
