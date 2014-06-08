import pygame as pg
from .. import tools, setup
from .. import constants as c


class ItemBox(pg.sprite.Sprite):
    """
    Item box for powerups.
    """
    def __init__(self, x, y):
        super(ItemBox, self).__init__()
        self.name = 'item box'
        self.get_image = tools.get_image
        self.image_list = self.make_image_list()
        self.index = 0
        self.image = self.image_list[self.index]
        self.rect = self.image.get_rect(x=x, bottom=y)
        self.state_dict = self.make_state_dict()
        self.state = c.NORMAL
        self.timer = 0.0
        self.first_half = True
        self.y_vel = 0
        self.start_y = y
        self.opened_image = self.make_opened_image()

    def make_image_list(self):
        """
        Make the list of images for item box animation.
        """
        spritesheet = setup.GFX['spritesheet1']
        image_list = []

        for i in range(3):
            x = 490 - (i * 70)
            y = 490
            width = 70
            height = 70
            image_list.append(self.get_image(x, y, width, height, spritesheet))

        return image_list

    def make_state_dict(self):
        """
        Make the state dictionary.
        """
        state_dict = {c.NORMAL: self.normal_state,
                      c.BUMPED: self.bumped_state,
                      c.OPENED: self.opened_state}

        return state_dict

    def make_opened_image(self):
        """
        Make the image when the box has been opened.
        """
        sprite_sheet = setup.GFX['spritesheet1']
        return self.get_image(280, 490, 70, 70, sprite_sheet)

    def update(self, current_time):
        """
        Update Item box based on state function.
        """
        state_function = self.state_dict[self.state]
        state_function(current_time)

    def normal_state(self, current_time):
        """
        Update when box in normal state.
        """
        self.animate(current_time)


    def animate(self, current_time):
        self.image = self.image_list[self.index]

        if self.first_half:
            if self.index == 0:
                if (current_time - self.timer) > 375:
                    self.index += 1
                    self.timer = current_time
            elif self.index < 2:
                if (current_time - self.timer) > 125:
                    self.index += 1
                    self.timer = current_time
            elif self.index == 2:
                if (current_time - self.timer) > 125:
                    self.index -= 1
                    self.first_half = False
                    self.timer = current_time
        else:
            if self.index == 1:
                if (current_time - self.timer) > 125:
                    self.index -= 1
                    self.first_half = True
                    self.timer = current_time


    def bumped_state(self, *args):
        """
        Update when box in bumped state.
        """
        self.image = self.opened_image

    def opened_state(self, *args):
        """
        Update when box in opened state.
        """
        self.image = self.opened_image

    def enter_bump(self):
        """
        Transition item box into bumped state.
        """
        self.y_vel = c.BUMP_SPEED
        self.state = c.BUMPED

    def enter_opened_state(self):
        """
        Transition item box into bumped state.
        """
        self.rect.bottom = self.start_y
        self.y_vel = 0
        self.state = c.OPENED


class BouncyStar(pg.sprite.Sprite):
    """
    Powerup to give our hero a bouncy power.
    """
    def __init__(self, x, y):
        super(BouncyStar, self).__init__()
        self.name = 'bouncy star'
        self.image = setup.GFX['star']
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.y_vel = 0
        self.start_y = y
        self.y_vel = c.BUMP_SPEED
        self.state = c.REVEAL

    def enter_revealed_state(self):
        """
        Star enters a stationary state.
        """
        self.y_vel = 0
        self.state = c.REVEALED
        self.rect.bottom = self.start_y









