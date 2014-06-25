import pygame as pg 
import constants as c 


class _Physics(object):
    """A simplified physics class. Psuedo-gravity is often good enough."""
    def __init__(self):
        """You can experiment with different gravity here."""
        self.x_vel = self.y_vel = 0
        self.grav = 0.4
        self.fall = False

    def physics_update(self):
        """If the player is falling, add gravity to the current y velocity."""
        if self.fall:
            self.y_vel += self.grav
        else:
            self.y_vel = 0

class _State(object):
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.done = False
        self.next = None
        self.previous = None
        self.game_data = {}

    def get_event(self, event):
        pass

    def startup(self, current_time, game_data):
        self.game_data = game_data
        self.start_time = current_time

    def cleanup(self):
        self.done = False
        return self.game_data

    def update(self, surface, keys, current_time, dt):
        pass

def get_images(sheet, size):
    frames = []
    frames.append(sheet.subsurface(27, 2, 16, 21))
    frames.append(sheet.subsurface(49, 2, 16, 21))
    frames.append(sheet.subsurface(71, 2, 16, 21))
    return frames