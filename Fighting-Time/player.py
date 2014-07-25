import pygame as pg 
import constants as c 
from spritesheet_functions import SpriteSheet 

class Player(pg.sprite.Sprite):
    def __init__(self, x, y, blockers):
        super(Player, self).__init__()
        self.sheet = SpriteSheet('p1_walk.png')
        self.image = self.sheet.get_image(4, 2, 17, 21)
        self.image.set_colorkey(c.SPRITESHEET_BACKGROUND)
        self.rect = self.image.get_rect(x=x, y=y)
        self.x_vel = 0
        self.y_vel = 0
        self.blockers = blockers

        self.grav = 0.4
        self.speed = c.PLAYER_SPEED

        self.collide_below = False

        # player state stuffs
        self.state_dict = self.make_state_dict()
        self.state = c.STANDING
        self.allow_jump = False

    def make_state_dict(self):
        state_dict = {c.STANDING: self.standing,
                    c.WALKING: self.walking,
                    c.FREE_FALL: self.free_fall}
        return state_dict

    def standing(self, keys):
        """Standing state."""
        if keys[pg.K_RIGHT]:
            self.direction = c.RIGHT 
            self.state = c.WALKING
        elif keys[pg.K_LEFT]:
            self.direction = c.LEFT 
            self.state = c.WALKING
        if keys[pg.K_SPACE] and self.allow_jump:
            self.jump()

        if not keys[pg.K_SPACE]:
            self.allow_jump = True

    def walking(self, keys):
        """Walking state."""
        if keys[pg.K_RIGHT]:
            self.direction = c.RIGHT
        elif keys[pg.K_LEFT]:
            self.direction = c.LEFT
        if keys[pg.K_SPACE] and self.allow_jump:
            self.jump()

        if not keys[pg.K_SPACE]:
            self.allow_jump = True

    def free_fall(self, keys):
        """Jumping state."""
        if keys[pg.K_RIGHT]:
            self.direction = c.RIGHT
        elif keys[pg.K_LEFT]:
            self.direction = LEFT

    def jump(self):
        self.state = c.FREE_FALL
        self.y_vel = c.START_JUMP_VEL

    def physics_update(self):
        """If player is falling, add gravity to the current y velocity."""
        if self.fall:
            self.y_vel += self.grav
        else:
            self.y_vel = 0

    def check_keys(self, keys):
        self.x_vel = 0
        if keys[pg.K_LEFT]:
            self.x_vel -= self.speed
        if keys[pg.K_RIGHT]:
            self.x_vel += self.speed
        if keys[pg.K_SPACE]:
            self.jump()

    def check_collisions(self, blockers):
        self.rect.x += self.x_vel
        for blocker in blockers:
            if self.rect.colliderect(blocker):
                self.rect.x -= self.x_vel
                self.x_vel = 0

        self.rect.y += self.y_vel
        for blocker in blockers:
            if self.rect.colliderect(blocker):
                self.rect.y -= self.y_vel
                self.y_vel = 0

    def check_falling(self, blockers):
        """If player is not touching ground, enter fall state."""
        if not self.collide_below:
            self.fall = True

    def check_below(self, blockers):
        self.rect.move_ip((0,1))
        collide = pg.sprite.spritecollide(self, blockers, False)
        self.rect.move_ip((0,-1))
        return collide

    def calc_grav(self):
        if self.y_vel == 0:
            self.y_vel = 1
        else: 
            self.y_vel += .5

        if self.rect.y >= c.SCREEN_SIZE[1] - self.rect.height and self.y_vel >= 0:
            self.y_vel = 0
            self.rect.y = c.SCREEN_SIZE[1] - self.rect.height

    def update(self, keys):
        state_function = self.state_dict[self.state]
        state_function(keys)
        """self.calc_grav()
        self.check_keys(keys)
        self.check_collisions(self.blockers)"""

    def draw(self, surface):
        """
        Blit player image to screen.
        """
        surface.blit(self.image, self.rect)