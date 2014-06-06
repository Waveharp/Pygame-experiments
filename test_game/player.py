""" This module holds the Player class. """
import pygame
import constants

from platforms import MovingPlatform
from spritesheet_functions import *

class Player(pygame.sprite.Sprite):
    # attributes
    # speed vector of Player
    change_x = 0
    change_y = 0

    # holds all images for animated walk left/right of Player
    initial_r = []
    initial_l = []
    walking_frames_l = []
    walking_frames_r = []

    # what direction is player facing?
    direction = "R"

    # list of sprites we can bump
    level = None

    # stuff for enlarging sprite:
    size = 0
    factor = 3

    # -- Methods
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        sprite_sheet = SpriteSheet("spritesheet.png")
        # Load all right facing images into a list
        image = sprite_sheet.get_image(441, 2, 17, 21)
        self.initial_r.append(image)
        image = sprite_sheet.get_image(464, 2, 16, 21)
        self.initial_r.append(image)
        image = sprite_sheet.get_image(486, 2, 18, 21)
        self.initial_r.append(image)
        image = sprite_sheet.get_image(601, 2, 18, 21)
        self.initial_r.append(image)
        image = sprite_sheet.get_image(624, 2, 18, 21)
        self.initial_r.append(image)
        image = sprite_sheet.get_image(648, 2, 16, 21)
        self.initial_r.append(image)
        image = sprite_sheet.get_image(671, 2, 16, 21)
        self.initial_r.append(image)
        
        # Load all the right facing images, then flip them
        # to face left.
        for image in self.initial_r:
            image = pygame.transform.flip(image, True, False)
            self.initial_l.append(image)

        for image in self.initial_r:
            image.set_colorkey(constants.SPRITESHEET_BACKGROUND)
            size = image.get_size()
            bigger_img = pygame.transform.scale(image, (int(size[0]*self.factor),
                                                        int(size[1]*self.factor)))
            self.walking_frames_r.append(bigger_img)

        for image in self.initial_l:
            image.set_colorkey(constants.SPRITESHEET_BACKGROUND)
            size = image.get_size()
            bigger_img = pygame.transform.scale(image, (int(size[0]*self.factor),
                                                        int(size[1]*self.factor)))
            self.walking_frames_l.append(bigger_img)

        # set starting player image
        self.image = self.walking_frames_r[0]

        # set reference to image rect
        self.rect = self.image.get_rect()


    def update(self):
        """ Move the player. """
        # gravity
        self.calc_grav()

        # move left/right
        self.rect.x += self.change_x
        pos = self.rect.x + self.level.world_shift
        if self.direction == "R":
            frame = (pos // 30) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]
        else:
            frame = (pos // 30) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]

        # see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # if we're moving right,
            # set right side to left side of item hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # if moving left, do the opposite
                self.rect.left = block.rect.right

        # move up/down
        self.rect.y += self.change_y

        # check for collisions
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # reset position based on top/bottom of object
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
 
            # Stop our vertical movement
            self.change_y = 0
 
            if isinstance(block, MovingPlatform):
                self.rect.x += block.change_x

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

        # see if we are on the ground
        if self.rect.y >= constants.SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = constants.SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ called when user hits jump button """
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # if it is ok to jump, set speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= constants.SCREEN_HEIGHT:
            self.change_y = -10

    # player-controlled movement
    def go_left(self):
        self.change_x = -6
        self.direction = "L"

    def go_right(self):
        self.change_x = 6
        self.direction = "R"

    def stop(self):
        self.change_x = 0