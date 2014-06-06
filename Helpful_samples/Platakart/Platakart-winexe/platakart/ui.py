# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

from pymunk.vec2d import Vec2d
from collections import OrderedDict
from pubsub import pub
import pymunktmx.pygame_util
import pyscroll
import pygame

from platakart.sprite import SpaceSprite
from platakart.sprite import ViewportSpriteMixin

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)


# This is probably not the best place for Scene, but putting it here
# helps to avoid forward declarations in core.py.
class Scene(object):
    def get_name(self):
        raise NotImplemented

    def setup(self, **kwargs):
        raise NotImplemented

    def teardown(self):
        pass

    def update(self, delta):
        pass

    def draw(self, surface, rect):
        pass


class Menu(pygame.sprite.OrderedUpdates):
    def __init__(self, rect=None, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)

        # rect is used to determine if menu should be scrolled or not
        # can be None, but menus will not scroll
        self._rect = rect

        self._cursor = 0
        self._focused_element = None

        # this should be in config, or generic catch-all events implemented
        self._player_prefix = "player%d" % 1

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = pygame.Rect(value)

    def collidepoint(self, pos):
        for spr in self.sprites():
            if spr.rect.collidepoint(pos):
                return spr
        return None

    def get_index(self, sprite):
        return self._spritelist.index(sprite)

    def setup(self, **kwargs):
        pub.subscribe(self.on_mouse_down, "input.mouse-down")
        pub.subscribe(self.on_mouse_up, "input.mouse-up")
        pub.subscribe(self.on_mouse_move, "input.mouse-move")
        pub.subscribe(self.on_right, self._player_prefix + "-right")
        pub.subscribe(self.on_left, self._player_prefix + "-left")
        pub.subscribe(self.on_up, self._player_prefix + "-up")
        pub.subscribe(self.on_down, self._player_prefix + "-down")
        pub.subscribe(self.on_button0, self._player_prefix + "-button0")
        pub.subscribe(self.on_button1, self._player_prefix + "-button1")

    def teardown(self):
        pub.unsubscribe(self.on_mouse_down, "input.mouse-down")
        pub.unsubscribe(self.on_mouse_up, "input.mouse-up")
        pub.unsubscribe(self.on_mouse_move, "input.mouse-move")
        pub.unsubscribe(self.on_right, self._player_prefix + "-right")
        pub.unsubscribe(self.on_left, self._player_prefix + "-left")
        pub.unsubscribe(self.on_up, self._player_prefix + "-up")
        pub.unsubscribe(self.on_down, self._player_prefix + "-down")
        pub.unsubscribe(self.on_button0, self._player_prefix + "-button0")
        pub.unsubscribe(self.on_button1, self._player_prefix + "-button1")

    def on_mouse_down(self, pos, button):
        element = self.collidepoint(pos)
        if element:
            self._focused_element = element
            element.select()

    def on_mouse_up(self, pos, button):
        element = self.collidepoint(pos)
        if element:
            if self._focused_element is element:
                element.choose()
                element.enabled = False

    def on_mouse_move(self, pos, rel, buttons):
        element = self.collidepoint(pos)
        if element:
            if self._focused_element is element:
                element.select()
            else:
                self.set_cursor(self.get_index(element))
        else:
            element = self.get_focused_element()
            if element:
                if element.pressed:
                    element.deselect()
                    self._focused_element = None
                else:
                    element.focus()

    def on_right(self, tilt_percent):
        if tilt_percent:
            self.set_cursor(self._cursor + 1)

    def on_left(self, tilt_percent):
        if tilt_percent:
            self.set_cursor(self._cursor - 1)

    # TODO: when menu is a grid, then this will have to add row number
    def on_up(self, tilt_percent):
        if tilt_percent:
            self.set_cursor(self._cursor - 1)

    # TODO: when menu is a grid, then this will have to add row number
    def on_down(self, tilt_percent):
        if tilt_percent:
            self.set_cursor(self._cursor + 1)

    def get_focused_element(self):
        sprites = self.sprites()
        if sprites:
            return sprites[self._cursor % len(sprites)]
        return None

    def set_cursor(self, value, force=False):

        # if the index is the same, just return
        if value == self._cursor and not force:
            return None

        element = self.get_focused_element()
        if element is None:
            return
        element.unfocus()

        # this prevents focus change while select button is pressed
        if self._focused_element is element:
            element.deselect()
            self._focused_element = None

        self._cursor = value
        element = self.get_focused_element()

        # this will move all of the elements to scroll past the menu
        if not self.rect.contains(element.rect):
            new_rect = element.rect.clamp(self.rect)
            dx = element.rect.left - new_rect.left
            dy = element.rect.top - new_rect.top
            for spr in self.sprites():
                spr.rect = spr.rect.move(-dx, -dy)

        element.focus()

        pub.sendMessage("menu.changed", element=element)
        pub.sendMessage("game.stop-sound", name="menu-switch")
        pub.sendMessage("game.play-sound", name="menu-switch")

    def on_button0(self, tilt_percent):
        element = self.get_focused_element()
        if tilt_percent:
            self._focused_element = element
            element.select()
        elif self._focused_element is element:
            element.choose()
            element.enabled = False

    # TODO: should this be the back/cancel button?
    def on_button1(self, tilt_percent):
        pass

    def add_internal(self, sprite):
        super(Menu, self).add_internal(sprite)

        # used to focus the 1st element added
        if len(self._spritelist) == 1:
            self.set_cursor(0, True)


class Button(pygame.sprite.DirtySprite):
    def __init__(self, id, pos, up_surf, down_surf, focus_surf):
        super(Button, self).__init__()
        self.id = id
        self.up_surf = up_surf
        self.down_surf = down_surf
        self.focus_surf = focus_surf
        self.image = self.up_surf
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self._enabled = True
        self.pressed = False

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = bool(value)

    def select(self):
        """ when element is pressed, but not released """
        if self.enabled and not self.pressed:
            self.pressed = True
            self.image = self.down_surf
            self.rect = self.rect.move(0, 4)
            self.dirty = 1

    def deselect(self):
        """ when element was selected, but no longer is """
        if self.enabled and self.pressed:
            self.pressed = False
            self.image = self.up_surf
            self.rect = self.rect.move(0, -4)
            self.dirty = 1

    def choose(self):
        """ when user wants to make this selection """
        if self.enabled:
            if self.pressed:
                self.deselect()
            pub.sendMessage("game.play-sound", name="menu-select")
            pub.sendMessage("button.clicked", id=self.id)

    def focus(self):
        """ when element is focued (like mouse hover or cursor) """
        self.image = self.focus_surf
        self.dirty = 1

    def unfocus(self):
        """ when element was focused, but no longer is """
        self.image = self.up_surf
        self.dirty = 1


class ViewPortGroup(pygame.sprite.Group):
    """ viewports can be attached
    """

    def __init__(self, space, map_data, resources):
        super(ViewPortGroup, self).__init__()
        self.space = space
        self.map_data = map_data
        self.resources = resources
        self.viewports = OrderedDict()
        self.rect = None

    def setup(self):
        pass

    def set_rect(self, rect):
        self.rect = rect
        self.resize()

    def resize(self):
        rects = list()
        if len(self.viewports) == 1:
            w, h = self.rect.size
            rects = [
                (0, 0, w, h),
            ]

        elif len(self.viewports) == 2:
            w, h = self.rect.size
            rects = [
                (0, 0, w, h / 2),
                (0, h / 2, w, h / 2),
            ]

        elif len(self.viewports) == 3:
            w, h = self.rect.size
            rects = [
                (0, 0, w, h / 2),
                (0, h / 2, w / 2, h / 2),
                (w / 2, h / 2, w / 2, h / 2),
            ]

        elif len(self.viewports) == 4:
            w = self.rect.width / 2
            h = self.rect.height / 2
            rects = [
                (0, 0, w, h),
                (w, 0, w, h),
                (0, h, w, h),
                (w, h, w, h),
            ]
        else:
            logger.error(
                "too many viewports in the manager. only 4 are allowed.")
            raise ValueError

        for k in self.viewports.keys():
            rect = pygame.Rect(rects.pop())
            k.set_rect(rect)
            self.viewports[k] = rect

    def update(self, delta):
        super(ViewPortGroup, self).update(delta)
        for vp in self.viewports:
            vp.update(delta)

    def draw(self, surface, rect):
        if rect is not self.rect:
            self.set_rect(rect)
        return [vp.draw(surface, r) for vp, r in self.viewports.items()]

    def add_internal(self, sprite):
        if isinstance(sprite, ViewPort):
            self.viewports[sprite] = None
            if self.rect is not None:
                self.resize()
        else:
            super(ViewPortGroup, self).add_internal(sprite)

    def remove_internal(self, sprite):
        if sprite in self.viewports:
            del self.viewports[sprite]
            if self.rect is not None:
                self.resize()
        else:
            super(ViewPortGroup, self).remove_internal(sprite)

    def clear(self):
        """ will not handle this
        """
        raise NotImplementedError


class ViewPort(pygame.sprite.Sprite):
    """ Draws a simulation
    """

    def __init__(self):
        super(ViewPort, self).__init__()
        self.parent = None
        self.rect = None
        self.camera_vector = None
        self.map_layer = None
        self.map_height = None
        self.following = None
        self.wireframe_mode = False

    def setup(self):
        pass

    def teardown(self):
        pass

    def set_rect(self, rect):
        self.rect = rect
        md = self.parent.map_data
        self.map_layer = pyscroll.BufferedRenderer(md, rect.size)
        self.map_height = md.height * md.tileheight
        self.center()

    def add_internal(self, group):
        try:
            assert(isinstance(group, ViewPortGroup))
        except AssertionError:
            raise

        super(ViewPort, self).add_internal(group)
        self.parent = group

    def follow(self, body):
        self.following = body

    def center(self):
        if self.rect is None:
            return

        if self.following:
            v = Vec2d(self.following.position)
            v.y = self.map_height - v.y
            self.camera_vector = v

        if self.camera_vector:
            self.map_layer.center(self.camera_vector)

    def update(self, delta):
        self.center()

    def draw(self, surface, rect):
        if rect is not self.rect:
            self.set_rect(rect)

        dirty = list()

        # TODO: test wireframe mode
        if self.wireframe_mode:
            self.buffer.set_clip(self.rect)
            self.buffer.fill(BLACK, self.rect)
            pymunktmx.pygame_util.draw(self.buffer,
                                       self.parent.tmx_data,
                                       self.parent.space)
            surface.blit(self.buffer)
        else:
            ox, oy = self.rect.topleft
            self.map_layer.draw(surface, self.rect)
            xx = -self.camera_vector.x + self.map_layer.half_width + ox
            yy = -self.camera_vector.y + self.map_layer.half_height + oy

            camera = self.rect.copy()
            camera.center = self.camera_vector

            # deref for speed
            surface_blit = surface.blit
            dirty_append = dirty.append
            camera_collide = camera.colliderect
            map_height = self.map_height

            for sprite in self.parent.sprites():

                # handle translation based on sprite sub-class
                if isinstance(sprite, SpaceSprite):
                    sprite.update_image()
                    new_rect = sprite.rect.copy()
                    new_rect.y = map_height - new_rect.y - new_rect.height
                    if camera_collide(new_rect):
                        new_rect = new_rect.move(xx, yy)
                        dirty_rect = surface_blit(sprite.image, new_rect)
                        dirty_append(dirty_rect)
                elif isinstance(sprite, ViewportSpriteMixin):
                    sprite.update_image()
                    new_rect = sprite.rect.copy()
                    dirty_append(surface_blit(
                        sprite.image, new_rect.move(*self.rect.topleft)))

        # TODO: dirty updates
        return self.rect


def labeled_button(id, label, font, pos, up_surf, down_surf, focus_surf):
    up_surf = up_surf.copy()
    down_surf = down_surf.copy()
    focus_surf = focus_surf.copy()
    rect = up_surf.get_rect()
    label_surf = font.render(label, True, WHITE)
    label_rect = label_surf.get_rect()
    label_rect.center = rect.center
    up_surf.blit(label_surf, label_rect)
    down_surf.blit(label_surf, label_rect)
    focus_surf.blit(label_surf, label_rect)
    return Button(id, pos, up_surf, down_surf, focus_surf)
