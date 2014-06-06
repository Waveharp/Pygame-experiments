from math import degrees
from pygame.transform import rotate, flip
import pygame


class SpaceSprite(pygame.sprite.Sprite):
    """
    Platakart Sprites

    platakart sprites draw themselves
    """
    def __init__(self, shape, surface):
        super(SpaceSprite, self).__init__()
        self.shape = shape
        self.original_surface = surface
        self._flipped = False
        if self.original_surface:
            self.rect = surface.get_rect()
            self.image = surface.copy()

    @property
    def position(self):
        return self.shape.body.position

    @property
    def flipped(self):
        return self._flipped

    # TODO: make available for y flip
    @flipped.setter
    def flipped(self, value):
        if self.original_surface:
            if self._flipped or value:
                image = flip(self.original_surface, 1, 0)
                self.original_surface = image.convert()

        self._flipped = bool(value)

    def update_image(self):
        """
        call this before drawing
        """
        image = rotate(self.original_surface, degrees(self.shape.body.angle))
        self.image = image.convert()
        self.rect = image.get_rect()
        self.rect.center = self.shape.body.position


class CircleSprite(SpaceSprite):
    """
    Sprite attached to Pymunk.Circle Shape
    """
    pass


class BoxSprite(SpaceSprite):
    """
    Sprite attached to Pymunk.Box Shape
    """
    pass


class SegmentSprite(SpaceSprite):
    """
    Sprite attached to Pymunk.Segment Shape
    """
    pass


class ViewportSpriteMixin(object):
    """
    Translation for Viewport coordinate space
    """
    pass
