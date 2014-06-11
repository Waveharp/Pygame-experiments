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

player = Player()

player.rect.x = 30
player.rect.y = c.SCREEN_HEIGHT - player.rect.height

active_sprite_list = pg.sprite.Group()
active_sprite_list.add(player)


"""Load tmx file from current dir, create 
tile_renderer object and load tmx file. """
tmx_file = os.path.join(os.getcwd(), 'test.tmx')
tile_renderer = tilerender.Renderer(tmx_file)

"""Create the map surface using the make_map()
method. Used to blit onto main_surface. """
map_surface = tile_renderer.make_map()
map_rect = map_surface.get_rect()



"""Simple game loop that blits the map_surface onto
main_surface."""
while True:
	main_surface.blit(map_surface, map_rect)

	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			sys.exit()

		if event.type == pg.KEYDOWN:
			if event.key == pg.K_LEFT:
				player.go_left()
			if event.key == pg.K_RIGHT:
				player.go_right()
			if event.key == pg.K_UP:
				player.jump()
		if event.type == pg.KEYUP:
			if event.key == pg.K_LEFT and player.change_x < 0:
				player.stop()
			if event.key == pg.K_RIGHT and player.change_x > 0:
				player.stop()


	active_sprite_list.update()
	active_sprite_list.draw(main_surface)
	pg.display.update()
	fps_clock.tick(50)

# background: 0, -63. width = 231 height = 63