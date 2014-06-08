"""
Handle game collisions.
"""
import math
import random
import pygame as pg
from . import constants as c
from .sprites import powerup
from . import tools, setup


class CollisionHandler(object):
    """
    Handles collisions between the player, enemies and game
    objects.
    """
    def __init__(self, player, sprites, blockers, enemy_blockers, item_boxes, stars, dead_group1, dead_group2, level,
                 doors):
        self.player = player
        self.sprites = sprites
        self.stars = stars
        self.blockers = blockers
        self.enemy_blockers = enemy_blockers
        self.item_boxes = item_boxes
        self.doors = doors
        self.dead_group1 = dead_group1
        self.dead_group2 = dead_group2
        self.state_dict = self.make_state_dict()
        self.current_time = 0.0
        self.level = level

    def make_state_dict(self):
        """
        Make dictionary for collision handler states.
        """
        state_dict = {c.WALKING: self.update_walking_player,
                      c.FREE_FALL: self.update_player_in_freefall,
                      c.STANDING: self.update_walking_player,
                      c.BOUNCY: self.update_player_in_freefall}

        return state_dict

    def update(self, keys, current_time, dt):
        state_function = self.state_dict[self.player.state]
        state_function(keys, dt, current_time)
        self.check_if_dead()

    def update_walking_player(self, keys, dt, current_time):
        """
        Move player when walking
        """
        self.current_time = current_time
        self.adjust_horizontal_motion(keys)
        self.player.rect.x += self.player.x_vel * dt
        self.check_for_collision(False, True)

        if self.player.x_vel > 0:
            if self.player.x_vel <= 25.0:
                self.player.enter_standing()
        else:
            if self.player.x_vel >= -25.0:
                self.player.enter_standing()

        self.check_for_ground(self.player)
        self.adjust_item_box_position(dt)
        self.adjust_sprite_position(dt)
        self.adjust_powerup_position(dt)

    def update_player_in_freefall(self, keys, dt, current_time):
        """
        Move player while jumping
        """
        self.current_time = current_time
        self.adjust_horizontal_motion(keys, False)

        self.player.rect.x += self.player.x_vel * dt
        self.check_for_collision(False, True)
        self.player.rect.y += self.player.y_vel * dt
        self.check_for_collision(True)

        if self.player.y_vel < c.MAX_FALL_SPEED:
            self.player.y_vel += c.GRAVITY * dt

        self.adjust_item_box_position(dt)
        self.adjust_powerup_position(dt)
        self.adjust_sprite_position(dt)


    def check_for_collision(self, vertical=False, horiz=False):
        """
        Check for ground and other blockers while in air.
        """
        blocker = pg.sprite.spritecollideany(self.player, self.blockers)
        item_box = pg.sprite.spritecollideany(self.player, self.item_boxes)
        bouncy_star = pg.sprite.spritecollideany(self.player, self.stars, tools.rect_than_mask)
        enemy = pg.sprite.spritecollideany(self.player, self.sprites)
        door = pg.sprite.spritecollideany(self.player, self.doors)

        if blocker and vertical:
            self.adjust_blocker_collision(self.player, blocker, True)
        elif blocker and horiz:
            self.adjust_blocker_collision(self.player, blocker, False, True)

        if item_box and vertical:
            self.adjust_blocker_collision(self.player, item_box, True)
        elif item_box and horiz:
            self.adjust_blocker_collision(self.player, item_box, False, True)

        if bouncy_star:
            setup.SFX['powerup'].play()
            bouncy_star.kill()
            self.player.enter_bouncy_state(self.current_time)

        if enemy and vertical:
            self.handle_enemy_collision_with_player(enemy, True)
        elif enemy and horiz:
            self.handle_enemy_collision_with_player(enemy, False, True)

        if door:
            self.level.end_game()

    def adjust_blocker_collision(self, sprite, collider, vertical=False, horiz=False):
        """
        Adjust for collision with item boxes.
        """
        if vertical:
            if sprite.y_vel > 0:
                sprite.rect.bottom = collider.rect.top
                if sprite.state == c.BOUNCY:
                    setup.SFX['enemykill'].play()
                    sprite.y_vel = c.START_JUMP_VEL
                else:
                    sprite.enter_walking()
            elif sprite.y_vel < 0:
                sprite.rect.top = collider.rect.bottom
                sprite.y_vel = 0
                if collider.state == c.NORMAL and collider.name == 'item box':
                    setup.SFX['powerup'].play()
                    collider.enter_bump()
        if horiz:
            if sprite.x_vel > 0:
                sprite.rect.right = collider.rect.left
            elif sprite.x_vel < 0:
                sprite.rect.left = collider.rect.right

    def check_for_ground(self, sprite):
        """
        Check for ground when walking off ledge.
        """
        sprite.rect.y += 1

        collideables = pg.sprite.Group(self.blockers, self.item_boxes)

        if not pg.sprite.spritecollideany(sprite, collideables):
            sprite.enter_fall()

        sprite.rect.y -= 1

    def adjust_horizontal_motion(self, keys, on_ground=True):
        """
        Adjust horizontal motion.
        """
        if not self.player.damaged:
            if keys[pg.K_RIGHT]:
                self.player.direction = c.RIGHT
                self.player.x_vel += (self.player.max_speed - self.player.x_vel) * .1

            elif keys[pg.K_LEFT]:
                self.player.direction = c.LEFT
                self.player.x_vel -= (self.player.max_speed + self.player.x_vel) * .1

            else:
                if on_ground:
                    self.ground_deceleration()


    def ground_deceleration(self):
        """
        Slow down character on ground.
        """
        if self.player.x_vel > 0:
            self.player.x_vel += (0 - self.player.x_vel) * .075
        elif self.player.x_vel < 0:
            self.player.x_vel += (0 - self.player.x_vel) * .075

    def adjust_item_box_position(self, dt):
        """
        Adjust item_box position based on y_vel.
        """
        for item_box in self.item_boxes:
            if item_box.state == c.BUMPED:
                item_box.y_vel += c.BUMP_GRAVITY * dt
                item_box.rect.y += item_box.y_vel * dt
                if item_box.rect.bottom > item_box.start_y:
                    item_box.enter_opened_state()
                    x = item_box.rect.centerx
                    y = item_box.rect.top
                    bouncy_star = powerup.BouncyStar(x, y)
                    self.stars.add(bouncy_star)

    def adjust_powerup_position(self, dt):
        """
        Adjust the position of star powerups based on y_vel.
        """
        for star in self.stars:
            if star.state == c.REVEAL:
                star.y_vel += c.BUMP_GRAVITY * dt
                star.rect.y += star.y_vel * dt
                if star.rect.bottom > star.start_y:
                    star.enter_revealed_state()

    def adjust_sprite_position(self, dt):
        """
        Adjust the position of each sprite based on velocity.
        """
        for sprite in self.sprites:
            if (self.player.rect.x - 475) <= sprite.rect.x <= (self.player.rect.x + 475):
                if not sprite.state == c.DEAD_ON_GROUND:
                    if sprite.state == c.FREE_FALL or sprite.state == c.IN_AIR:
                        sprite.y_vel += c.GRAVITY * dt
                    if sprite.x_vel < 0:
                        horiz_adjust = int(math.floor(sprite.x_vel * dt))
                    else:
                        horiz_adjust = int(math.ceil(sprite.x_vel * dt))

                    sprite.rect.x += horiz_adjust
                    self.check_for_enemy_horiz_collision(sprite)
                    sprite.rect.y += sprite.y_vel * dt
                    self.check_for_enemy_vertical_collision(sprite)
                    if sprite.state == c.WALKING:
                        self.check_for_ground(sprite)

    def check_for_enemy_horiz_collision(self, enemy):
        collideable = pg.sprite.Group(self.blockers, self.item_boxes, self.enemy_blockers)
        collider = pg.sprite.spritecollideany(enemy, collideable)

        if collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = collider.rect.left
                enemy.direction = c.LEFT
                enemy.x_vel *= -1
            elif enemy.direction == c.LEFT:
                enemy.rect.left = collider.rect.right
                enemy.direction = c.RIGHT
                enemy.x_vel *= -1


    def check_for_enemy_vertical_collision(self, enemy):
        collideable = pg.sprite.Group(self.blockers, self.item_boxes)
        collider = pg.sprite.spritecollideany(enemy, collideable)


        if collider:
            if enemy.y_vel > 0:
                x = enemy.rect.x
                if enemy.state == c.IN_AIR:
                    enemy.enter_dead_on_ground_state()
                    enemy.rect.x = x
                    enemy.rect.bottom = collider.rect.top + 12

                else:
                    enemy.enter_walking()
                    enemy.rect.bottom = collider.rect.top

            elif enemy.y_vel < 0:
                enemy.rect.top = collider.rect.bottom
                enemy.y_vel = 0

    def handle_enemy_collision_with_player(self, enemy, vertical=False, horiz=True):
        """
        Handle collisions between enemy and player.
        """
        if self.player.state == c.BOUNCY:
            if enemy.state == c.WALKING:
                if random.randint(1,2) == 1:
                    enemy.hit_by_player(self.dead_group1)
                else:
                    enemy.hit_by_player(self.dead_group2)
        else:
            if enemy.state == c.WALKING:
                setup.SFX['hurt'].play()
                if vertical:
                    self.player.rect.bottom = enemy.rect.top
                    if self.player.rect.centerx < enemy.rect.centerx:
                        self.player.damaged_by_enemy(c.LEFT)
                        if enemy.direction == c.LEFT:
                            enemy.x_vel *= -1
                        enemy.direction = c.RIGHT
                    elif self.player.rect.centerx >= enemy.rect.centerx:
                        self.player.damaged_by_enemy(c.RIGHT)
                        if enemy.direction == c.RIGHT:
                            enemy.x_vel *= -1
                        enemy.direction = c.LEFT
                elif horiz:
                    if self.player.rect.centerx < enemy.rect.centerx:
                        self.player.rect.right = enemy.rect.left
                        self.player.damaged_by_enemy(c.LEFT)
                        if enemy.direction == c.LEFT:
                            enemy.x_vel *= -1
                        enemy.direction = c.RIGHT
                    elif self.player.rect.centerx >= enemy.rect.centerx:
                        self.player.rect.left = enemy.rect.right
                        self.player.damaged_by_enemy(c.RIGHT)
                        if enemy.direction == c.RIGHT:
                            enemy.x_vel *= -1
                        enemy.direction = c.LEFT

    def check_if_dead(self):
        if self.player.rect.y > self.player.level_bottom:
            self.level.game_data[c.LIVES] -= 1
            if self.level.game_data[c.LIVES] <= 0:
                self.level.next = c.GAME_OVER
            else:
                self.level.next = c.LIVES_LEFT
            self.level.done = True
















