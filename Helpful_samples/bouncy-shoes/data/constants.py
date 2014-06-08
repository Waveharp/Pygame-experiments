import pygame as pg

#COLORS

BLACK =  0, 0, 0
WHITE = 255, 255, 255

#GAME STATES
LEVEL1 = 'level1'
MAIN_MENU = 'main menu'
CONTROLS = 'controls'
LIVES_LEFT = 'lives left'
GAME_OVER = 'game over'


#LEVEL STATES
NORMAL = 'normal'

#Player states
STANDING = 'standing'
WALKING = 'walking'
FREE_FALL = 'free fall'
BOUNCY = 'bouncy'
AUTOWALK = 'autowalk'

#PLAYER values
SLOWEST_FREQUENCY = 100
START_JUMP_VEL = -1120
GRAVITY = 2520
RUN_SPEED = 600
WALK_SPEED = 350
SLOW_WALK_SPEED = 100
BOUNCE_TIME = 5000
MAX_FALL_SPEED = 2000

#FONTS
MAIN_FONT = 'DroidSans'

#Directions

RIGHT = 'right'
LEFT = 'left'

#CONTROLS

JUMP_BUTTON = pg.K_a
RUN_BUTTON = pg.K_s

#ITEM BOX STATE
BUMPED = 'bumped'
OPENED = 'opened'
BUMP_SPEED = -1000
BUMP_GRAVITY = 6000

#ITEM STATES
REVEAL = 'reveal'
REVEALED = 'revealed'

#ENEMY DEATH STATES
IN_AIR = 'in air'
DEAD_ON_GROUND = 'dead on ground'

LIVES = 'lives'