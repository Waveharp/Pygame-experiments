import pygame
import constants
import levels
from pytmx import tmxloader
from bullets import Bullet
from player import Player


def main():
	""" Main function for the game. """
	pygame.init()
	
	# set width, height of screen
	size = [constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT]
	screen = pygame.display.set_mode(size)
	
	pygame.display.init()
	pygame.display.set_caption("Game of Badassdom")


	player = Player()

	level_list = []
	level_list.append(levels.Level_01(player))

	current_level_no = 0
	current_level = level_list[current_level_no]
	
	active_sprite_list = pygame.sprite.Group()
	player.level = current_level

	player.rect.x = 340
	player.rect.y = constants.SCREEN_HEIGHT - player.rect.height
	active_sprite_list.add(player)

	bullet_list = pygame.sprite.Group()

	# loop until user clicks close button
	done = False
	
	clock = pygame.time.Clock()
	# --- Main Program Loop ---
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					player.go_left()
				if event.key == pygame.K_RIGHT:
					player.go_right()
				if event.key == pygame.K_UP:
					player.jump()
				if event.key == pygame.K_SPACE:
					bullet = Bullet()
					bullet.rect.x = player.rect.x
					bullet.rect.y = player.rect.y
					active_sprite_list.add(bullet)
					bullet_list.add(bullet)
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT and player.change_x < 0:
					player.stop()
				if event.key == pygame.K_RIGHT and player.change_x > 0:
					player.stop()

		active_sprite_list.update()
		current_level.update()
				
		current_level.draw_tiles(0, 0, screen)
		active_sprite_list.draw(screen)
		
		clock.tick(60)

		pygame.display.flip()
		
	pygame.quit()
	
if __name__ == "__main__":
	main()
