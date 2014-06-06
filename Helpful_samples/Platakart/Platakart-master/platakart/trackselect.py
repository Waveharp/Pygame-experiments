# -*- coding: utf-8; -*-

from collections import namedtuple
from random import sample
import logging
import string

from pubsub import pub
import pygame.display
import pygame.font
import pygame.sprite

logger = logging.getLogger("platakart.trackselect")

from platakart.ui import BLACK
from platakart.ui import BLUE
from platakart.ui import WHITE
from platakart.ui import Button
from platakart.ui import Scene
from platakart.ui import Menu


TrackInfo = namedtuple("TrackInfo", "key, name, description, thumbnail")


def track_button(font, pos, thumb_surf, track_info):
    up_surf = thumb_surf.copy()
    thumb_rect = up_surf.get_rect().inflate(-1, -1)
    pygame.draw.rect(up_surf, BLACK, thumb_rect, 2)
    focus_surf = up_surf.copy()
    highlight_rect = focus_surf.get_rect().inflate(-24, -24)
    pygame.draw.rect(focus_surf, BLUE, highlight_rect, 8)
    track_info = track_info
    rect = thumb_surf.get_rect()
    label_surf = font.render(track_info.name, True, WHITE)
    label_rect = label_surf.get_rect()
    label_rect.center = rect.center
    up_surf.blit(label_surf, label_rect)
    focus_surf.blit(label_surf, label_rect)
    button = Button(track_info, pos, up_surf, up_surf, focus_surf)
    button.track_info = track_info
    return button


class TrackSelectScene(Scene):
    def __init__(self, resources):
        Scene.__init__(self)
        self.resources = resources
        self.rendered = False
        self.font = None
        self.menu = None
        self.rect = None
        self.background = None
        self.group = None
        self.info_sprite = None
        self.title_sprite = None
        self.redraw_info = False
        self.options = None
        self.reloadable = True

    def get_name(self):
        return "track-select"

    def setup(self, options):
        self.options = options
        logger.debug("Setting up kart select scene")
        screen = pygame.display.get_surface()
        screen_rect = screen.get_rect()
        self.font = pygame.font.SysFont("Verdana", 32)
        self.menu = Menu(screen_rect)
        self.menu.setup()
        self.group = pygame.sprite.RenderUpdates()
        self.options = options

        self.title_sprite = pygame.sprite.Sprite()
        self.info_sprite = pygame.sprite.Sprite()

        pub.subscribe(self.on_button_clicked, "button.clicked")
        pub.subscribe(self.on_menu_changed, "menu.changed")

        # values calc'd by using the screen ratio 640x480
        x = int(screen_rect.width * .03125)
        y = int(screen_rect.width * .03334)
        pos = [x, y]
        for key, tilemap in self.resources.tilemaps.items():
            info = TrackInfo(key, tilemap.name, tilemap.description,
                             tilemap.thumbnail)
            image = self.resources.images[info.thumbnail]

            # values calc'd by using the screen ratio 640x480
            size = int(screen_rect.width * .2)
            image = pygame.transform.scale(image, (size, size))

            self.menu.add(track_button(self.font, pos, image, info))
            pos[1] += image.get_rect().height + 30

    def teardown(self):
        logger.debug("Tearing down track select scene")
        pub.unsubscribe(self.on_button_clicked, "button.clicked")
        pub.unsubscribe(self.on_menu_changed, "menu.changed")
        self.menu.teardown()

    def update(self, delta):
        if self.menu:
            self.menu.update(delta)

    def draw(self, surface, rect):
        dirty = list()

        if self.rect is not rect:
            self.rect = rect

        if not self.background:
            self.background = pygame.Surface(rect.size)
            image = self.resources.images["track-select"]
            pygame.transform.scale(image, rect.size, self.background)
            surface.blit(self.background, rect)
            dirty.append(rect)

        if self.redraw_info:
            self.on_menu_changed(self.menu.get_focused_element())
            self.redraw_info = False

        self.group.clear(surface, self.background)
        dirty.extend(self.group.draw(surface))

        self.menu.clear(surface, self.background)
        dirty.extend(self.menu.draw(surface))

        return dirty

    def on_menu_changed(self, element):

        # the menu will get instanced before the scene can set the rect,
        # so, this will create a flag so the track infor will be redrawn
        # when needed.
        if self.rect is None:
            self.redraw_info = True
            return

        track_info = element.track_info

        self.title_sprite.kill()
        self.info_sprite.kill()

        # values calc'd by using the surface ratio 640x480
        x = int(self.rect.width * .3125)
        y = int(self.rect.height * .167)

        self.title_sprite = pygame.sprite.Sprite()
        image = self.font.render(track_info.name, True, WHITE).convert_alpha()
        rect = image.get_rect().move((x, y))
        self.title_sprite.image = image
        self.title_sprite.rect = rect

        max_width = 0
        height = 0
        lines = []
        for i, line in enumerate(track_info.description.split("|")):
            text = line.strip()
            surf = self.font.render(text, True, WHITE)
            w, h = self.font.size(text)
            height += h
            if w > max_width:
                max_width = w
            lines.append(surf)

        image = pygame.Surface((max_width, height), flags=pygame.SRCALPHA)
        for index, line in enumerate(lines):
            image.blit(line, (0, index * (height/len(lines))))

        # values calc'd by using the surface ratio 640x480
        x = int(self.rect.width * .3125)
        y = int(self.rect.height * .167) + 64

        self.info_sprite = pygame.sprite.Sprite()
        self.info_sprite.image = image
        self.info_sprite.rect = image.get_rect().move((x, y))

        self.group.add(self.info_sprite, self.title_sprite)

    def on_button_clicked(self, id):
        logger.debug("Track {%s} selected" % id.key)

        # set the track
        self.options["trackname"] = id.key

        pub.sendMessage("game.switch-scene",
                        name="track",
                        options=self.options)
