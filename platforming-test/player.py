import pygame as pg 
import constants as c 
import tools
from spritesheet_functions import SpriteSheet 

class Player(tools._Physics, pg.sprite.Sprite):
    """Class representing our player."""
    def __init__(self,location,speed):
        """
        The location is an (x,y) coordinate pair, and speed is the player's
        speed in pixels per frame. Speed should be an integer.
        """
        tools._Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        self.sheet = SpriteSheet("spritesheet.png")
        self.image = self.sheet.get_image(441, 2, 17, 21)
        self.image.set_colorkey(c.SPRITESHEET_BACKGROUND)
        self.rect = self.image.get_rect(topleft=location)
        self.direction = "RIGHT"
        self.speed = speed
        self.jump_power = -9.0
        self.jump_cut_magnitude = -3.0
        self.on_moving = False
        self.collide_below = False

    def get_walking_frames(self):
        self.walking_frames = []
        sheet = SpriteSheet('p1_walk.png')
        self.walking_frames.append(27, 2, 16, 21)
        self.walking_frames.append(49, 2, 16, 21)
        self.walking_frames.append(71, 2, 16, 21)

    def check_keys(self, keys):
        """Find the player's self.x_vel based on currently held keys."""
        self.x_vel = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.x_vel -= self.speed
            self.direction = "LEFT"
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.x_vel += self.speed
            self.direction = "RIGHT"

    def get_position(self, obstacles):
        """Calculate the player's position this frame, including collisions."""
        if not self.fall:
            self.check_falling(obstacles)
        else:
            self.fall = self.check_collisions((0,self.y_vel), 1, obstacles)
        if self.x_vel:
            self.check_collisions((self.x_vel,0), 0, obstacles)

    def check_falling(self, obstacles):
        """If player is not contacting the ground, enter fall state."""
        if not self.collide_below:
            self.fall = True
            self.on_moving = False

    def check_moving(self,obstacles):
        """
        Check if the player is standing on a moving platform.
        If the player is in contact with multiple platforms, the prevously
        detected platform will take presidence.
        """
        if not self.fall:
            now_moving = self.on_moving
            any_moving, any_non_moving = [], []
            for collide in self.collide_below:
                if collide.type == "moving":
                    self.on_moving = collide
                    any_moving.append(collide)
                else:
                    any_non_moving.append(collide)
            if not any_moving:
                self.on_moving = False
            elif any_non_moving or now_moving in any_moving:
                self.on_moving = now_moving

    def check_collisions(self, offset, index, obstacles):
        """
        This function checks if a collision would occur after moving offset
        pixels. If a collision is detected, the position is decremented by one
        pixel and retested. This continues until we find exactly how far we can
        safely move, or we decide we can't move.
        """
        unaltered = True
        self.rect[index] += offset[index]
        while pg.sprite.spritecollideany(self, obstacles):
            self.rect[index] += (1 if offset[index]<0 else -1)
            unaltered = False
        return unaltered

    def check_above(self, obstacles):
        """When jumping, don't enter fall state if there is no room to jump."""
        self.rect.move_ip(0, -1)
        collide = pg.sprite.spritecollideany(self, obstacles)
        self.rect.move_ip(0, 1)
        return collide

    def check_below(self, obstacles):
        """Check to see if the player is contacting the ground."""
        self.rect.move_ip((0,1))
        collide = pg.sprite.spritecollide(self, obstacles, False)
        self.rect.move_ip((0,-1))
        return collide

    def jump(self, obstacles):
        """Called when the user presses the jump button."""
        if not self.fall and not self.check_above(obstacles):
            self.y_vel = self.jump_power
            self.fall = True
            self.on_moving = False

    def jump_cut(self):
        """Called if player releases the jump key before maximum height."""
        if self.fall:
            if self.y_vel < self.jump_cut_magnitude:
                self.y_vel = self.jump_cut_magnitude

    def pre_update(self, obstacles):
        """Ran before platforms are updated."""
        self.collide_below = self.check_below(obstacles)
        self.check_moving(obstacles)

    def update(self, obstacles, keys):
        """Everything we need to stay updated; ran after platforms update."""
        self.check_keys(keys)
        self.get_position(obstacles)
        self.physics_update()
        
    def draw(self, surface):
        """Blit the player to the target surface."""
        surface.blit(self.image, self.rect)

