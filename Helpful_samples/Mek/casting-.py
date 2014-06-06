import os
import sys
import math
import pygame as pg


CAPTION = "Casting"
SCREEN_SIZE = (500, 500)
BACKGROUND_COLOR = (30, 40, 50)


class Block(pg.sprite.Sprite):
    """Just your average block here."""
    def __init__(self, pos, size, color, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = pg.Surface(size).convert()
        self.rect = self.image.get_rect(topleft=pos)
        self.hit_color = pg.Color("tomato")
        self.safe_color = color
        self.hit = False

    def update(self):
        """Color is changed to the hit color if hit."""
        color = (self.hit_color if self.hit else self.safe_color)
        self.image.fill(color)


class Control(object):
    """Prepare program; choose a start point; and create some blocks; run."""
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = 'True'
        pg.init()
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.start_point = self.screen_rect.center
        self.blocks = self.make_blocks()

    def make_blocks(self):
        """
        Create some arbitrary blocks of arbitrary color and arbitrary position.
        """
        blocks = pg.sprite.Group()
        blocks.add(Block((50,75), (40,40), pg.Color("blue")),
                   Block((200,370), (40,10), pg.Color("green")),
                   Block((400,50), (25,25), pg.Color("grey")),
                   Block((375,250), (30,100), pg.Color("yellow")),
                   Block((20,420), (50,50), pg.Color("cyan")))
        return blocks

    def event_loop(self):
        """Lettuce leaf?"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True

    def cast(self):
        """
        Project a line from the start point in the direction of the mouse,
        incrementing by a unit-pixel per iteration.  If the test point detects
        a collision, set that as the end point; else project until off the
        screen.
        """
        mouse = pg.mouse.get_pos()
        x_comp = mouse[0]-self.start_point[0]
        y_comp = mouse[1]-self.start_point[1]
        magnitude = math.hypot(y_comp, x_comp)
        unit = x_comp/magnitude, y_comp/magnitude
        test_point = [self.start_point[0]+unit[0], self.start_point[1]+unit[1]]
        casting = True
        while casting:
            next_point = [test_point[0]+unit[0], test_point[1]+unit[1]]
            if not self.screen_rect.collidepoint(next_point):
                casting = False
            else:
                for block in self.blocks:
                    if block.rect.collidepoint(next_point):
                        casting = False
                        block.hit = True
                        break
                    else:
                        block.hit = False
                else:
                    test_point = next_point
        self.end_point = test_point

    def update(self):
        """Cast line and update blocks."""
        self.cast()
        self.blocks.update()

    def draw(self):
        """Fill screen; draw cast line; and draw blocks."""
        self.screen.fill(BACKGROUND_COLOR)
        pg.draw.aaline(self.screen, pg.Color("white"),
                       self.start_point, self.end_point)
        self.blocks.draw(self.screen)

    def display_fps(self):
        """Show the programs FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """Run run run."""
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
            self.display_fps()


if __name__ == "__main__":
    Control().main_loop()
    pg.quit()
    sys.exit()