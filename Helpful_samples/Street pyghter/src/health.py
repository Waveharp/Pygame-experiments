import pygame
from pygame.locals import *
from game import Point

class EnergyBar:
    def __init__(self, orientation = True):
        self.energy = 0
        if orientation:
            self.position = Point(8, 221)
        else:
            self.position = Point(212, 221)
        self.orientation = orientation
        self.front = pygame.image.load('../res/energyfront.png').convert_alpha()
        self.back = pygame.image.load('../res/energyback.png').convert_alpha()
        self.flash = True
        self.flash_count = 0
    
    def add(self, int):
        self.energy += int
        if self.energy > 96:
            self.energy = 96
    
    def consume(self):
        if self.energy > 23:
            self.energy -= 24
            return True
        else: return False
    
    def print_me(self, screen):
        surface = pygame.Surface((self.energy, 7)).convert()
        surface.fill((235,220,30))
        screen.blit(self.back, self.position.value())
        if self.orientation:
            point = self.position + (5,4)
            point2 = point
        else:
            point = self.position + (101-self.energy,4)
            point2 = self.position + (101-(self.energy//24)*24,4)
        screen.blit(surface, point.value())
        surface = pygame.Surface(((self.energy//24)*24, 7)).convert()
        if self.flash:
            surface.fill((255,255,200))
        else: surface.fill((255,240,30))
        if self.flash_count == 0:
            self.flash = not self.flash
        else:
            if self.flash_count > 1:
                self.flash_count = -1
        self.flash_count += 1
        screen.blit(surface, point2.value())
        screen.blit(self.front, self.position.value())
        

class HealthBar:
    def __init__(self, maxhealth, orientation = True):
        self.health = self.maxHealth = maxhealth
        if orientation:
            self.position = Point(8, 8)
        else:
            self.position = Point(170, 8)
        self.orientation = orientation
        self.hp = 142
        self.trail = 142
        self.tick = 0
    
    def loseHp(self, damage, damage_reduce):
        if damage_reduce > 0:
            if damage_reduce > 0.8:
                damage_reduce = 0.8
            damage -= damage*damage_reduce
        if self.health < self.maxHealth/2:
            if self.health < self.maxHealth*3/10:
                if self.health < self.maxHealth*3/20:
                    damage -= damage*25/100 # reduction to 75% when under 15%
                else: damage -= damage*20/100 # reduction to 80% when under 25%
            else: damage -= damage*10/100 # reduction to 90% when under 50%
        if damage < 2:
                damage = 2
#        print("damage = ", damage, damage_reduce)
        self.health -= damage
        if self.health < 0:
            self.health = 0
        if self.health > self.maxHealth:
            self.health = self.maxHealth
        self.hp = int((self.health/self.maxHealth) * 142)
    
    def reinit(self):
        self.health = self.maxHealth
        self.hp = 142
        self.trail = 142
    
    def tick_me(self, int):
        if self.tick < int:
            self.tick += 1
            return
        if self.trail > self.hp:
            self.trail -= 1
        self.tick = 0
    
    def amIdead(self):
        return self.health == 0
    
    def print_me(self, screen):
        surface = pygame.Surface((self.trail, 7)).convert()
        surface.fill((255,90,30))
        if self.orientation:
            screen.blit(surface, (self.position+(142-self.trail, 0)).value())
        else : screen.blit(surface, self.position.value())
        surface = pygame.Surface((self.hp, 7)).convert()
        surface.fill((255,240,30))
        if self.orientation:
            screen.blit(surface, (self.position+(142-self.hp, 0)).value())
        else : screen.blit(surface, self.position.value())
        