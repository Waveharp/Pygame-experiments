"""
Main controllable player.
"""
from __future__ import division
import copy
import pygame as pg
from .. import tools, setup
from .. import constants as c


class Player(pg.sprite.Sprite):
    """
    User controlled player.
    """
    def __init__(self, x, y, level):
        super(Player, self).__init__()
        self.get_image = tools.get_image
        self.state_dict = self.make_state_dict()
        self.state = c.STANDING
        self.walking_image_dict = self.make_walking_image_dict()
        self.standing_image_dict = self.make_standing_image_dict()
        self.jumping_image_dict = self.make_jumping_image_dict()
        self.index = 0
        self.timer = 0.0
        self.bouncy_timer = 0.0
        self.direction = c.RIGHT
        self.x_vel = 0
        self.y_vel = 0
        self.tint_alpha = 255
        self.damage_alpha = 255
        self.max_speed = c.WALK_SPEED
        self.allow_jump = False
        self.damaged = False
        self.image = self.standing_image_dict[self.direction]
        self.rect = self.image.get_rect(x=x, bottom=y)
        self.level_bottom = level.level_rect.bottom

    def make_state_dict(self):
        """
        Make the dictionary of state methods for player.
        """
        state_dict = {c.STANDING: self.standing,
                      c.WALKING: self.walking,
                      c.FREE_FALL: self.free_fall,
                      c.BOUNCY: self.bouncing,
                      c.AUTOWALK: self.auto_walk}
        return state_dict

    def standing(self, keys, current_time, dt):
        """
        State when player is still.
        """
        self.image = self.standing_image_dict[self.direction]

        if keys[pg.K_RIGHT]:
            self.index = 0
            self.direction = c.RIGHT
            self.state = c.WALKING
            self.timer = current_time
        elif keys[pg.K_LEFT]:
            self.index = 0
            self.direction = c.LEFT
            self.state = c.WALKING
            self.timer = current_time
        if keys[c.JUMP_BUTTON] and self.allow_jump:
            self.enter_jump()

        if not keys[c.JUMP_BUTTON]:
            self.allow_jump = True

    def walking(self, keys, current_time, dt):
        """
        State when player is walking.
        """
        self.damaged = False
        self.image_list = self.walking_image_dict[self.direction]
        self.image = self.image_list[self.index]
        self.animate(current_time, dt)

        if keys[pg.K_RIGHT]:
            self.direction = c.RIGHT
        elif keys[pg.K_LEFT]:
            self.direction = c.LEFT
        if keys[c.JUMP_BUTTON] and self.allow_jump:
            self.enter_jump()
        if keys[c.RUN_BUTTON]:
            self.max_speed = c.RUN_SPEED
        elif not keys[c.RUN_BUTTON]:
            self.max_speed = c.WALK_SPEED

        if not keys[c.JUMP_BUTTON]:
            self.allow_jump = True

    def animate(self, current_time, dt):
        """
        Animate sprite.
        """
        if (current_time - self.timer) > self.get_animation_speed(dt):
            self.timer = current_time
            if self.index < (len(self.image_list) - 1):
                self.index += 1
            else:
                self.index = 0

    def get_animation_speed(self, dt):
        """
        Calculate frame frequency by x_vel.
        """
        if self.x_vel == 0:
            frequency = c.SLOWEST_FREQUENCY
        elif self.x_vel > 0:
            frequency = c.SLOWEST_FREQUENCY - (self.x_vel * 11 * dt)
        else:
            frequency = c.SLOWEST_FREQUENCY - (self.x_vel * dt * 11 * -1)

        return frequency

    def enter_jump(self):
        """
        Set values to enter jump state.
        """
        self.state = c.FREE_FALL
        self.y_vel = c.START_JUMP_VEL

    def free_fall(self, keys, *args):
        """
        Jumping state.
        """
        self.image = self.jumping_image_dict[self.direction]
        if keys[pg.K_RIGHT]:
            self.direction = c.RIGHT
        elif keys[pg.K_LEFT]:
            self.direction = c.LEFT
        self.damage_fade()

    def bouncing(self, keys, current_time, *args):
        """
        Bouncing state.
        """
        self.free_fall(keys)

        if keys[c.RUN_BUTTON]:
            self.max_speed = c.RUN_SPEED
        elif not keys[c.RUN_BUTTON]:
            self.max_speed = c.WALK_SPEED

        if (current_time - self.bouncy_timer) > c.BOUNCE_TIME:
            self.state = c.FREE_FALL

        self.color_fade()

    def color_fade(self):
        """
        Fade a color tint based on player height.
        """
        self.image = copy.copy(self.jumping_image_dict[self.direction])
        tinted_image = copy.copy(self.image).convert_alpha()
        tinted_image.fill((0, 255, 0, self.tint_alpha), special_flags=pg.BLEND_RGBA_MULT)
        self.image.blit(tinted_image, (0, 0))

        if self.y_vel <= 0:
            percent = (self.y_vel / c.START_JUMP_VEL)
        else:
            percent = 0
        self.tint_alpha = int(255 * percent)
        if self.tint_alpha < 0:
            self.tint_alpha = 0
        elif self.tint_alpha > 255:
            self.tint_alpha = 255

    def damage_fade(self):
        """
        Turn red tint when damaged.
        """
        if self.damaged:
            self.image = copy.copy(self.jumping_image_dict[self.direction])
            tinted_image = copy.copy(self.image).convert_alpha()
            tinted_image.fill((255, 0, 0, self.damage_alpha), special_flags=pg.BLEND_RGBA_MULT)
            self.image.blit(tinted_image, (0, 0))
            self.damage_alpha -= 5
            if self.damage_alpha < 0:
                self.damage_alpha = 0


    def make_walking_image_dict(self):
        """
        Make the list of walking animation images.
        """
        sprite_sheet = setup.GFX['p1_walking']

        right_images = self.make_walking_image_list(sprite_sheet)
        left_images = self.make_walking_image_list(sprite_sheet, True)

        walking_dict = {c.RIGHT: right_images,
                        c.LEFT: left_images}

        return walking_dict

    def make_walking_image_list(self, sprite_sheet, reverse_images=False):
        """
        Return a list of images for walking animation.
        """
        coord = []
        for y in range(2):
            for x in range(6):
                coord.append((x, y))

        walking_images = []
        for pos in coord:
            width = 72
            height = 97
            x = pos[0] * width
            y = pos[1] * height
            walking_images.append(self.get_image(x, y,
                                                 width, height,
                                                 sprite_sheet))
        walking_images.pop(-1)
        #walking_images.pop(-1)

        if reverse_images:
            flipped_images = []
            for image in walking_images:
                flipped_images.append(pg.transform.flip(image, True, False))
            return flipped_images
        else:
            return walking_images

    def make_standing_image_dict(self):
        """
        Make the list of the standing pose images.
        """
        right_image = setup.GFX['p1_stand']
        left_image = pg.transform.flip(right_image, True, False)

        return {c.RIGHT: right_image,
                c.LEFT: left_image}

    def make_jumping_image_dict(self):
        """
        Make the list of the jumping images.
        """
        sheet = setup.GFX['p1_jumping']
        right_image = self.get_image(0, 0, 66, 97, sheet)
        left_image = self.get_image(66, 0, 66, 97, sheet)

        return {c.RIGHT: right_image,
                c.LEFT: left_image}

    def update(self, keys, current_time, dt):
        state_function = self.state_dict[self.state]
        state_function(keys, current_time, dt)

    def enter_walking(self):
        """
        Transition into walking state.
        """
        self.allow_jump = False
        self.y_vel = 0
        self.state = c.WALKING

    def enter_standing(self):
        """
        Transition into standing state.
        """
        self.state = c.STANDING
        self.x_vel = 0

    def enter_fall(self):
        """
        Transition into standing state.
        """
        self.state = c.FREE_FALL
        self.y_vel = 0

    def enter_bouncy_state(self, current_time):
        """
        Transition into bouncy state.
        """
        self.bouncy_timer = current_time
        self.state = c.BOUNCY
        self.y_vel = c.START_JUMP_VEL

    def damaged_by_enemy(self, direction):
        """
        Transition into free fall state after being damaged by enemies.
        """
        self.state = c.FREE_FALL
        self.damaged = True
        self.damage_alpha = 255

        if direction == c.LEFT:
            self.x_vel = -200
        else:
            self.x_vel = 200
        self.y_vel = -700

    def auto_walk(self, keys, current_time, dt):
        self.image_list = self.walking_image_dict[self.direction]
        self.image = self.image_list[self.index]
        self.x_vel = 100
        self.animate(current_time, dt)
        self.direction = c.RIGHT

        self.rect.x += self.x_vel * dt





