"""
Basic moving platforms using only rectangle collision.

- Base code written by Sean J. McKiernan 'Mekire'
- Modified by Waveharp
"""

import os
import sys
import tools
import pygame as pg
import constants as c 
from spritesheet_functions import SpriteSheet 
from player import Player


class Control(object):
    """Class for managing event loop and game states."""
    def __init__(self):
        """Initalize the display and prepare game objects."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player((50,875), 4)
        self.viewport = self.screen.get_rect()
        self.level = pg.Surface((1000,1000)).convert()
        self.level_rect = self.level.get_rect()
        self.win_text,self.win_rect = self.make_text()
        self.obstacles = self.make_obstacles()

    def make_text(self):
        """Renders a text object. Text is only rendered once."""
        font = pg.font.Font(None, 100)
        message = "You win. Celebrate."
        text = font.render(message, True, (100,100,175))
        rect = text.get_rect(centerx=self.level_rect.centerx, y=100)
        return text, rect

    def make_obstacles(self):
        """Adds some arbitrarily placed obstacles to a sprite.Group."""
        walls = [Block(pg.Color("chocolate"), (0,980,1000,20)),
                 Block(pg.Color("chocolate"), (0,0,20,1000)),
                 Block(pg.Color("chocolate"), (980,0,20,1000))]
        static = [Block(pg.Color("darkgreen"), (250,780,200,100)),
                  Block(pg.Color("darkgreen"), (600,880,200,100)),
                  Block(pg.Color("darkgreen"), (20,360,880,40)),
                  Block(pg.Color("darkgreen"), (950,400,30,20)),
                  Block(pg.Color("darkgreen"), (20,630,50,20)),
                  Block(pg.Color("darkgreen"), (80,530,50,20)),
                  Block(pg.Color("darkgreen"), (130,470,200,215)),
                  Block(pg.Color("darkgreen"), (20,760,30,20)),
                  Block(pg.Color("darkgreen"), (400,740,30,40))]
        moving = [MovingBlock(pg.Color("olivedrab"), (20,740,75,20), 325, 0),
                  MovingBlock(pg.Color("olivedrab"), (600,500,100,20), 880, 0),
                  MovingBlock(pg.Color("olivedrab"),
                              (420,430,100,20), 550, 1, speed=3, delay=200),
                  MovingBlock(pg.Color("olivedrab"),
                              (450,700,50,20), 930, 1, start=930),
                  MovingBlock(pg.Color("olivedrab"),
                              (500,700,50,20), 730, 0, start=730),
                  MovingBlock(pg.Color("olivedrab"),
                              (780,700,50,20), 895, 0, speed=-1)]
        return pg.sprite.Group(walls, static, moving)

    def update_viewport(self):
        """
        The viewport will stay centered on the player unless the player
        approaches the edge of the map.
        """
        self.viewport.center = self.player.rect.center
        self.viewport.clamp_ip(self.level_rect)

    def event_loop(self):
        """We can always quit, and the player can sometimes jump."""
        for event in pg.event.get():
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump(self.obstacles)
            elif event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def update(self):
        """Update the player, obstacles, and current viewport."""
        self.keys = pg.key.get_pressed()
        self.player.pre_update(self.obstacles)
        self.obstacles.update(self.player, self.obstacles)
        self.player.update(self.obstacles, self.keys)
        self.update_viewport()

    def draw(self):
        """
        Draw all necessary objects to the level surface, and then draw
        the viewport section of the level to the display surface.
        """
        self.level.fill(pg.Color("lightblue"))
        self.obstacles.draw(self.level)
        self.level.blit(self.win_text, self.win_rect)
        self.player.draw(self.level)
        self.screen.blit(self.level, (0,0), self.viewport)

    def display_fps(self):
        """Show the programs FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(c.CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """As simple as it gets."""
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
            self.display_fps()


class Block(pg.sprite.Sprite):
    """A class representing solid obstacles."""
    def __init__(self, color, rect):
        """The color is an (r,g,b) tuple; rect is a rect-style argument."""
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(color)
        self.type = "normal"


class MovingBlock(Block):
    """A class to represent horizontally and vertically moving blocks."""
    def __init__(self, color, rect, end, axis, delay=500, speed=2, start=None):
        """
        The moving block will travel in the direction of axis (0 or 1)
        between rect.topleft and end. The delay argument is the amount of time
        (in miliseconds) to pause when reaching an endpoint; speed is the
        platforms speed in pixels/frame; if specified start is the place
        within the blocks path to start (defaulting to rect.topleft).
        """
        Block.__init__(self, color, rect)
        self.start = self.rect[axis]
        if start:
            self.rect[axis] = start
        self.axis = axis
        self.end = end
        self.timer = 0.0
        self.delay = delay
        self.speed = speed
        self.waiting = False
        self.type = "moving"

    def update(self, player, obstacles):
        """Update position. This should be done before moving any actors."""
        obstacles = obstacles.copy()
        obstacles.remove(self)
        now = pg.time.get_ticks()
        if not self.waiting:
            speed = self.speed
            start_passed = self.start >= self.rect[self.axis]+speed
            end_passed = self.end <= self.rect[self.axis]+speed
            if start_passed or end_passed:
                if start_passed:
                    speed = self.start-self.rect[self.axis]
                else:
                    speed = self.end-self.rect[self.axis]
                self.change_direction(now)
            self.rect[self.axis] += speed
            self.move_player(now, player, obstacles, speed)
        elif now-self.timer > self.delay:
            self.waiting = False

    def move_player(self, now, player, obstacles, speed):
        """
        Moves the player both when on top of, or bumped by the platform.
        Collision checks are in place to prevent the block pushing the player
        through a wall.
        """
        if player.on_moving is self or pg.sprite.collide_rect(self,player):
            axis = self.axis
            offset = (speed, speed)
            player.check_collisions(offset, axis, obstacles)
            if pg.sprite.collide_rect(self, player):
                if self.speed > 0:
                    self.rect[axis] = player.rect[axis]-self.rect.size[axis]
                else:
                    self.rect[axis] = player.rect[axis]+player.rect.size[axis]
                self.change_direction(now)

    def change_direction(self, now):
        """Called when the platform reaches an endpoint or has no more room."""
        self.waiting = True
        self.timer = now
        self.speed *= -1

if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(c.CAPTION)
    pg.display.set_mode(c.SCREEN_SIZE)
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()
