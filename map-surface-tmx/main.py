import sys, os
import pygame as pg
import tilerender
import constants as c
from player import Player

""" Init pygame, create clock, create window
with a surface to blit map onto. """
pg.init()
fps_clock = pg.time.Clock()
main_surface = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
main_rect = main_surface.get_rect()
pg.display.set_caption("Messin' with maps")


"""Load tmx file from current dir, create 
tile_renderer object and load tmx file. """
tmx_file = os.path.join(os.getcwd(), 'test.tmx')
tile_renderer = tilerender.Renderer(tmx_file)

"""Create the map surface using the make_map()
method. Used to blit onto main_surface. """
map_surface = tile_renderer.make_map()
map_rect = map_surface.get_rect()

"""Create a list of rects called "blockers" that the
player can collide with. The getObjects() method 
returns a list of objects in your tile map. Each 
tile has properties like name, type, x, y, width,
height.  Double click objects in Tiled to see these
properties.  These properties are used to make rect 
objects in Pygame."""
blockers = []
tilewidth = tile_renderer.tmx_data.tilewidth
for tile_object in tile_renderer.tmx_data.getObjects():
	properties = tile_object.__dict__
	if properties['name'] == 'blocker':
		x = properties['x']
		y = properties['y']
		width = properties['width']
		height = properties['height']
		new_rect = pg.Rect(x, y, width, height)
		blockers.append(new_rect)

player = Player(blockers)

"""Simple game loop that blits the map_surface onto
main_surface."""
while True:
	keys = pg.key.get_pressed()
	player.update(keys)
	main_surface.blit(map_surface, map_rect)
	player.draw(main_surface)

	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			sys.exit()

	pg.display.update()
	fps_clock.tick(50)

# background: 0, -63. width = 231 height = 63