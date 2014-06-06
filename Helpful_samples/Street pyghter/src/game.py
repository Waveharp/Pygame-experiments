import pygame, os
from pygame.locals import *
from math import hypot

class AnimationCounter:
    '''Compteur de l'animation de puis une SpriteSheet,
    garde une trace de l'animation (ligne) et la frame (colonne) en cours'''
    def __init__(self, animation, frame):
        self.curent_anim = animation
        self.frame = frame
        self.end_anim = True
        
    def set_anim(self, anim):
        if self.curent_anim != anim:
            self.curent_anim = anim
            self.frame = 0
            self.end_anim = False
    
    def __str__(self):
        return 'AnimationCounter (animation: {0}, frame: {1})'.format(self.curent_anim, self.frame)

class GameObject:
    def __init__(self, file, sprite_width, sprite_height, position):
        self.sprite_list = SpriteSheetLoader(file, sprite_width, sprite_height).getSpriteList()
        self.maxlength = self.getmaxlength()
        self.position = position
        self.animation = AnimationCounter(0,0)
        self.newFrame = True # sert pour ne pas repeter un coup sur plusieur frame
        self.tick = 0
        
    def tick_me(self, int):
        if self.tick<int:
            self.tick+=1
            return
        self.animation.frame += 1
        self.newFrame = True
        if (self.animation.frame >= len(self.getSpriteLine())):
            self.animation.frame = 0
            self.animation.end_anim = True
        if (self.getSprite() == None):
            self.animation.frame = 0
            self.animation.end_anim = True
        self.tick = 0
    
    def getmaxlength(self):
        length = 0
        for sprite_line in self.sprite_list:
            tmp = len(sprite_line)
            if  tmp > length:
                length = tmp
        return length
    
    def getSpriteLine(self):
        return self.sprite_list[self.animation.curent_anim]
    
    def getSprite(self):
        return self.getSpriteLine()[self.animation.frame]
    
    def print_me(self, screen):
        if self.getSprite() != None :
            screen.blit(self.getSprite(), self.position.value())

class GameObjectWithHitBox(GameObject):
    '''Demo object should be deleted in the futur'''
    def __init__(self, file, sprite_width, sprite_height, position):
        GameObject.__init__(self, file, sprite_width, sprite_height, position)
        hitbox_file = file.replace('.png', 'Rect.png')
        self.hitBox_list = RectangleSheetLoader(hitbox_file, sprite_width, sprite_height).getRectList()
    
    def getGameRectLine(self):
        return self.hitBox_list[self.animation.curent_anim]
    
    def getGameRect(self):
        return self.getGameRectLine()[self.animation.frame]
    
    def print_me(self, screen):
        if self.getSprite() != None :
            screen.blit(self.getSprite(), self.position.value())
        if self.getGameRect() != None :
            # afficher le rectangle
            self.getGameRect().print_me(screen, self.position.value())
            
class SpriteSheetLoader:
    def __init__(self,file,sprite_width,sprite_height, fullsheet=False):
        self.sheet = pygame.image.load(os.path.join(file))
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.sprite_list=self.makeSpritelist()
        if not fullsheet:
            self.removeBlanks(file)
        
    def getSpriteList(self):
        return self.sprite_list
    
    def getSpriteLines(self,*args):
        for arg in args:
            assert(isinstance(arg, int)) # assert it's an array index
            yield self.sprite_list[arg] # return the animation and get to the next one asked
    
    def makeSprite(self,line=0,column=0):
        sprite = pygame.Surface((self.sprite_width, self.sprite_height)).convert_alpha()
        sprite.fill((0,0,0,0))
        sprite.blit(self.sheet, (-(column*self.sprite_width),-(line*self.sprite_height)))
        return sprite
    
    def makeSpritelist(self):
        size = self.sheet.get_size()
        sprite_list=[]
        for i in range(int(size[1]/self.sprite_height)):    
            sprite_line=[]
            for j in range(int(size[0]/self.sprite_width)):
                sprite_line.append(self.makeSprite(i,j))
            sprite_list.append(sprite_line)
        return sprite_list
    
    def testBlankSprite(self,sprite):
        for i in range(self.sprite_width):
            for j in range(self.sprite_height):
                if sprite.get_at((i,j))!=(0,0,0,0):
                    return False
        return True
    
    def removeBlanks(self, file):
        try:
            with open(file.replace('.png', '.txt'), encoding='utf-8') as txtfile:
                i=0
                for line in txtfile:
                    length = int(line)
                    while length < len(self.sprite_list[i]):
                        self.sprite_list[i].pop()
                    i+=1
        except:
            print('creating...')    
            for sprite_line in self.sprite_list:
                j=0
                while j < len(sprite_line):
                    if self.testBlankSprite(sprite_line[j]):
                        sprite_line[j] = None
                    j+=1
            self.write(file)
            
    def write(self,file):
        txtfile = open(file.replace('.png', '.txt'), mode='w', encoding='utf-8')
        for sprite_line in self.sprite_list:
            i=0
            for sprite in sprite_line:
                if sprite == None:
                    break
                else: i+=1
            txtfile.write(str(i))
            txtfile.write('\n')
            
        
class RectangleSheetLoader:
    def __init__(self,file,sprite_width,sprite_height):
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.rectangle_list = []
        try:
            print('reading...'+file)
            with open(file.replace('.png', '.txt'), encoding='utf-8') as txtfile:
                for line in txtfile:
                    line = line.split('/')
                    rect_line = []
                    for rectangle in line:
                        if rectangle == '\n':
                            continue
                        elif rectangle == 'None':
                            rect_line.append(None)
                        else:
                            rectangle = rectangle.split('-')
                            assert(rectangle[0] == 'GR')
                            width = int(rectangle[1])
                            height = int(rectangle[2])
                            position = Point(int(rectangle[3]),int(rectangle[4]))
                            rect_line.append(GameRectangle(width, height, position))
                    self.rectangle_list.append(rect_line)
        except:
            print('creating...')
            self.sheet = pygame.image.load(os.path.join(file))
            self.rectangle_list=self.makeRectangleList()
            self.write(file)
    
    def write(self,file):
        txtfile = open(file.replace('.png', '.txt'), mode='w', encoding='utf-8')
        for line in self.rectangle_list:
            for element in line:
                if element == None:
                    txtfile.write('None')
                else:
                    txtfile.write(element.write())
                txtfile.write('/')
            txtfile.write('\n')
        
    def getRectList(self):
        return self.rectangle_list
    
    def detectRectangle(self, target_point, start_pixel):
        '''Trouve le rectangle a partir du point de départ de celui ci'''
        rect_start = target_point - start_pixel # le point de depart du rectangle dans la frame
        i = 1
        # tant que i est inferieur a la longueure restante du sprite
        while i <= start_pixel.x+self.sprite_width - target_point.x:
            # si le point suivant est vide ou qu'on est au bout
            if (self.sheet.get_at((target_point+(i,0)).value()) == (0,0,0,0)) or (i == start_pixel.x+self.sprite_width - target_point.x):
                j = 1
                # tant que j est inferieur a la hauteur restante ou qu'on est au bout
                while j <= start_pixel.y + self.sprite_height - target_point.y:
                    # si le point en-dessous est vide
                    if (self.sheet.get_at((target_point+(i-1,j)).value()) == (0,0,0,0)) or (j == start_pixel.y + self.sprite_height - target_point.y):
                        break
                    j += 1 # point suivant en-dessous
                break
            i += 1 # point suivant a cote
        return GameRectangle(i, j, rect_start)
                    
    
    def findRectangle(self,line=0,column=0):
        '''Repere le point de départ du rectangle et
        appelle la fonction de detection du rectangle
        retourne le rectangle'''
        start_pixel = Point(column*self.sprite_width,line*self.sprite_height)
        for j in range(self.sprite_height):
            for i in range(self.sprite_width):
                target_point = Point(i+start_pixel.x,j+start_pixel.y)
                if self.sheet.get_at(target_point.value())!=(0,0,0,0):
                    # target_point est alors le point de départ de notre rectangle dans la sprite_sheet
                    return self.detectRectangle(target_point, start_pixel)       
        return None
    
    def makeRectangleList(self):
        size = self.sheet.get_size()
        rectangle_list=[]
        for i in range(int(size[1]/self.sprite_height)):    
            rectangle_line=[]
            for j in range(int(size[0]/self.sprite_width)):
                rectangle_line.append(self.findRectangle(i,j))
            rectangle_list.append(rectangle_line)
        return rectangle_list
        
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def value(self):
        return (self.x, self.y)
    
    def __eq__(self,other):
        if isinstance(other, Point):
            return (self.x == other.x) and (self.y == other.y)
        else:
            return False
        
    def __add__(self, other):
        assert(isinstance(other, Point) or isinstance(other, Vector) or isinstance(other, tuple))
        if isinstance(other, tuple):
            return Point(self.x + other[0], self.y + other[1])
        else:
            return Point(self.x + other.x, self.y + other.y)
            
    def __sub__(self, other):
        assert(isinstance(other, Point) or isinstance(other, Vector) or isinstance(other, tuple))
        if isinstance(other, tuple):
            return Point(self.x - other[0], self.y - other[1])
        else:
            return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        assert(isinstance(other, int))
        return Point(self.x*other, self.y*other)
    
    def __floordiv__(self, other):
        return self.__truediv__(other)
            
    def __truediv__(self, other):
        assert(isinstance(other, int))
        return Point(self.x//other, self.y//other)
            
    def __str__(self):
        return "Point({0}, {1})".format(self.x, self.y)
    
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.length()
        
    def length(self):
        '''Sets and returns the vector's length as an integer,
        using the hypot methode of math.py'''
        self.length=hypot(self.x, self.y)
        self.length = int(self.length)
        return self.length
    
    def __eq__(self,other):
        if isinstance(other, Vector):
            return (self.x == other.x) and (self.y == other.y)
        else:
            return False
    
    def __add__(self, other):
        assert(isinstance(other, Point) or isinstance(other, Vector) or isinstance(other, tuple))
        if isinstance(other, tuple):
            return Vector(self.x + other[0], self.y + other[1])
        else:
            return Vector(self.x + other.x, self.y + other.y)
            
    def __sub__(self, other):
        assert(isinstance(other, Point) or isinstance(other, Vector) or isinstance(other, tuple))
        if isinstance(other, tuple):
            return Vector(self.x - other[0], self.y - other[1])
        else:
            return Vector(self.x - other.x, self.y - other.y)
        
    def __mul__(self, other):
        assert(isinstance(other, Vector) or isinstance(other, int))
        if isinstance(other, int):
            return Vector(other*self.x,other*self.y) ## retourne le vecteur multiple par un scalaire
        else:
            return  self.x*other.x+self.y*other.y ## retourne le produit scalaire
    
    def __floordiv__(self, other):
        assert(isinstance(other, int))
        return Vector(self.x/other, self.y/other) ## retourne le vecteur ayant subi une division scalaire
    
    def __truediv__(self, other):
        return self.__floordiv__(other)
        
    def __str__(self):
        return "Vector({0}, {1})".format(self.x, self.y)

class Vector2P (Vector):
    def __init__(self, start_point, end_point):
        Vector.__init__(self, 1, 1)
        self.x = end_point.x - start_point.x
        self.y = end_point.y - start_point.y
        self.length()

class MultiGameRectangles:
    pass

class GameRectangle:
    def __init__(self, width, height, position = Point(0,0)):
        self.width = width
        self.height = height
        if (isinstance(position, Point)):
            self.position = position
        else:
            assert(isinstance(position, tuple))
            assert(len(tuple) > 1)
            assert(isinstance(position[0],int) and isinstance(position[1],int))
            self.position = Point(position[0],position[1])
        self.area = self.width * self.height
    
    def value(self):
        return (self.width,self.height)
    
    def getCenter(self):
        return self.position + (self.width//2, self.height//2)
    
    def getasRect(self):
        return pygame.Rect(self.position.value(), self.value())
    
    def print_me(self, screen, color=(0,255,0,128)):
        surface = pygame.Surface((self.width, self.height)).convert_alpha()
        surface.fill(color)
        screen.blit(surface, (self.position).value())
    
    def write(self):
        return 'GR-{0}-{1}-{2}-{3}'.format(self.width, self.height, self.position.x, self.position.y)
        
    def __eq__(self,other):
        if isinstance(other, GameRectangle):
            return (self.width == other.width) and (self.height == other.height)
        else:
            return False
    
    def __str__(self):
        return "GameRectangle({0}, {1}) at {2}x{3}".format(self.width, self.height, self.position.x, self.position.y)

if __name__ == "__main__":
    
    print("start")
    pygame.init()
    screen = pygame.display.set_mode((320, 240), 0, 32)
    pygame.display.set_caption("Test") # program title
    clock = pygame.time.Clock()
    
    background = pygame.image.load('../res/ArcadeSized.png').convert()
    sprite_list = SpriteSheetLoader('../res/Ken.png', 60, 60).getSpriteList()
    gameobj = GameObjectWithHitBox('../res/Ken.png', 60, 60, Point(32,130))
    
    tick = 0
    
##    Print sprite_list dans la console
#    for sprite_line in sprite_list:
#        print(sprite_line)
    
    while True:
        
        ## Conditions d'arret du programme
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
        ## Fait defiler les animations
                if event.key == K_UP:
                    gameobj.animation.curent_anim += 1
                    gameobj.animation.frame = 0
                    if (gameobj.animation.curent_anim >= len(gameobj.sprite_list)):
                        gameobj.animation.curent_anim = 0
                if event.key == K_DOWN:
                    gameobj.animation.curent_anim -= 1
                    gameobj.animation.frame = 0
                    if (gameobj.animation.curent_anim < 0):
                        gameobj.animation.curent_anim = len(gameobj.sprite_list)-1
        
        time_passed = clock.tick(30)
        
        ## Ticking
        if (tick > 1):
            gameobj.tick_me()
            tick = 0
        else:
            tick += 1
        
        ## Rafraichissement de l'ecran
        screen.fill((0,0,0))
        ## Mise en place du decor
        screen.blit(background, (0,0))
        
        ## Affiche le GameObject
        gameobj.print_me(screen)
        
        ## Affiche la liste des sprites
        for i in range(len(sprite_list)):
            for j in range(len(sprite_list[i])):
                if sprite_list[i][j] != None:
                    screen.blit(sprite_list[i][j], (500 + (j*20), 32 + (i*30)))
        
        pygame.display.update()
    