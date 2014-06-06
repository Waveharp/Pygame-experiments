import pygame, os
from pygame.locals import *
from random import randint
from game import Point
import config
import Round
import game

class Fight_stats:
    def __init__(self):
        self.wins_P1 = 0
        self.rounds_P1 = 0
        self.wins_P2 = 0
        self.rounds_P2 = 0
        self.draws = 0
        self.lastwin = 0
    
    def update(self, tuple):
        rounds_P1, rounds_P2 = tuple[0], tuple[1]
        if rounds_P1 == rounds_P2:
            self.draws += 1
            self.lastwin = 0
        elif rounds_P1 > rounds_P2:
            self.wins_P1 +=1
            self.lastwin = 1
        else:
            self.wins_P2 +=1
            self.lastwin = 2
        self.rounds_P1 += rounds_P1
        self.rounds_P2 += rounds_P2

def getCharList():
    folder = '../res/Char'
    list = os.listdir(folder)
    for file in list:
        if not os.path.isdir(os.path.join(folder ,file)):
            list.remove(file)
    return list

def getBckgrndList():
    folder = '../res/Background'
    list = os.listdir(folder)
    list2 = os.listdir(folder)
    for file in list2:
        if os.path.isdir(os.path.join(folder ,file)) or file.find('Bckgrnd') < 0:
            list.remove(file)
    return list

class YesNo:
    def __init__(self, string, value = True, position = Point(0,0)):
        self.yes = Text(string+' : Yes', position).sprite
        self.no = Text(string+' : No', position).sprite
        self.choice = value
    
    def more(self):
        self.switch()
        
    def less(self):
        self.switch()
    
    def switch(self):
        self.choice = not self.choice
    
    def print_me(self, screen):
        if self.choice:
            screen.blit(self.yes, self.position.value())
        else:
            screen.blit(self.no, self.position.value())

class Value:
    def __init__(self, string, value = 2, maxValue = 5, position = Point(0,0)):
        self.maxValue = maxValue
        self.value = value
        self.position = position
        self.string = string+' : '
        self.sprite = self.convert()
        self.dot = pygame.image.load('../res/dot.png').convert_alpha()
        
    def convert(self):
        filled = pygame.image.load('../res/dotempty.png').convert_alpha()
        text = Text(self.string, self.position)
        self.length = len(self.string)
        sprite = pygame.Surface((15*(self.length+1+self.maxValue), 32)).convert_alpha()
        sprite.fill((0,0,0,0))
        sprite.blit(text.sprite, (0,0))
        for i in range(self.maxValue):
            sprite.blit(filled, (15*(self.length+self.maxValue-i), 0))
        return sprite
    
    def more(self):
        self.value += 1
        if self.value > self.maxValue:
            self.value = self.maxValue
            
    def less(self):
        self.value -= 1
        if self.value < 0:
            self.value = 0
        
    def print_me(self,screen):
        screen.blit(self.sprite, self.position.value())
        for i in range(self.value):
            position = self.position + (15*(self.length+1+i), 0)
            screen.blit(self.dot, position.value())

class KeyChoice:
    def __init__(self, string, position = Point(0,0), key = K_SPACE):
        string = string+' : '
        self.length = len(string)
        self.text = Text(string, position).sprite
        self.position = position
        self.keytext = Text(pygame.key.name(key), position).sprite
        self.key = key
    
    def more(self):
        self.key = None
        while self.key == None:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    self.key = event.key
                    self.keytext = Text(pygame.key.name(self.key)).sprite
        
    def less(self):
        return
    
    def print_me(self, screen):
        screen.blit(self.text, self.position.value())
        position = self.position + (140, 0)
        screen.blit(self.keytext, position.value())

class MultChoice:
    def __init__(self, string, options, value = 2, position = Point(0,0)):
        string = string+' : '
        self.length = len(string)
        self.text = Text(string, position).sprite
        self.position = position
        self.options = []
        for option in options:
            self.options.append(Text(option).sprite)
        self.choice = value
    
    def more(self):
        self.choice += 1
        if self.choice >= len(self.options):
            self.choice = 0
        
    def less(self):
        self.choice -= 1
        if self.choice < 0:
            self.choice = len(self.options)-1
    
    def print_me(self, screen):
        screen.blit(self.text, self.position.value())
        position = self.position + (15*self.length, 0)
        screen.blit(self.options[self.choice], position.value())

class Text:
    def __init__(self, string, position = Point(0,0)):
        self.string = string
        self.position = position
        self.letters = config.Alphabet().sprites
        self.sprite = self.convert()
        
    def convert(self):
        assert(isinstance(self.string,str))
        length = len(self.string)
        sprite = pygame.Surface((15*(length+1), 32)).convert_alpha()
        sprite.fill((0,0,0,0))
        for index in range(length):
            num = ord(self.string[index])
            line = num//16
            column = num-(line*16)
            letter = self.letters[line][column]
            if letter != None:
                sprite.blit(letter, (index*15, 0))
        return sprite
    
    def print_me(self, screen, position = Point(0,0)):
        screen.blit(self.sprite, (self.position+position).value())
            
class Menu:
    def __init__(self, position, screen, background = 'MenuScreen.png'):
        self.sprites = config.Alphabet().sprites
#        self.sprites = SpriteSheetLoader('../res/Ascii.png', 16, 16).getSpriteList()
        self.cursor = pygame.image.load('../res/cursor.png').convert_alpha()
        self.screen = screen
        self.options = []
        self.position = position
        self.choice = 1
        self.background = background
    
    def addElt(self, elt):
        if isinstance(elt, Text):
            position = self.position + (0, 3+len(self.options)*16)
        else:
            position = self.position + (15, 3+len(self.options)*16)
        elt.position = position
        self.options.append(elt)
    
    def back(self):
        return 0
        
    def mainloop(self):
        background = pygame.image.load('../res/Background/'+self.background).convert()
        while True:
        
            ## Conditions d'arret du programme
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        config.SoundPlayer().play_sound('menucancel.wav')
                        return self.back()
                    if event.key == K_UP:
                        config.SoundPlayer().play_sound('menumove.wav')
                        self.up()
                    if event.key == K_DOWN:
                        config.SoundPlayer().play_sound('menumove.wav')
                        self.down()
                    if event.key == K_RIGHT or event.key == K_RETURN:
                        config.SoundPlayer().play_sound('menuok.wav')
                        self.more()
                    if event.key == K_LEFT:
                        config.SoundPlayer().play_sound('menuok.wav')
                        self.less()
            
            ## Rafraichissement de l'ecran
            self.screen.fill((0,0,0))
            ## BG
            self.screen.blit(background, (0,0))
            
            ## Affiche le GameObject
            self.print_me()
            
            config.Screen().display_update(self.screen)
            
    def up(self):
        self.choice -= 1
        if self.choice < 0:
            self.choice = 0
        if isinstance(self.options[self.choice], Text):
            if self.choice == 0:
                self.down()
            else:
                self.up()
    
    def down(self):
        self.choice += 1
        if self.choice >= len(self.options):
            self.choice = len(self.options)-1
        if isinstance(self.options[self.choice], Text):
            if self.choice == len(self.options)-1:
                self.up()
            else:
                self.down()
    
    def more(self):
        option = self.options[self.choice]
        if isinstance(option, KeySetter):
            option.keymenu(self.screen)
        else: option.more()
    
    def less(self):
        self.options[self.choice].less()
    
    def print_me(self):
        cursor_pos = self.position + (3, self.choice*16)
        self.screen.blit(self.cursor, cursor_pos.value())
        for option in self.options:
            option.print_me(self.screen)
    
    def tick_me(self):
        pass

class MenuElt:
    def __init__(self, string, function, position = Point(0,0)):
        self.string = string
        self.position = position
        self.text = Text(string, position)
        self.function = function
    
    def print_me(self, screen):
        if self.position != self.text.position:
            self.text.position = self.position
        self.text.print_me(screen)
    
    def more(self):
        self.function()
    
    def less(self):
        return

class KeyMenu(Menu):
    def __init__(self, string,  screen, value):
        Menu.__init__(self, Point(20,10), screen, 'OptionScreen.png')
        self.waiting = pygame.image.load('../res/waiting.png')
        self.addElt(Text(string))
        self.addElt(KeyChoice('UP', key = value[0]))
        self.addElt(KeyChoice('DOWN', key = value[1]))
        self.addElt(KeyChoice('LEFT', key = value[2]))
        self.addElt(KeyChoice('RIGHT', key = value[3]))
        self.addElt(KeyChoice('BTN_A', key = value[4]))
        self.addElt(KeyChoice('BTN_B', key = value[5]))
        self.addElt(KeyChoice('BTN_C', key = value[6]))
    
    def back(self):
        ## get all keys
        value = []
        for option in self.options:
            if isinstance(option, KeyChoice):
                value.append(option.key)
        return value
    
    def more(self):
        self.screen.blit(self.waiting, (0,0))
        config.Screen().display_update(self.screen)
        Menu.more(self)
        self.down()



class KeySetter:
    def __init__(self, string, value = [32,32,32,32,32,32,32], position = Point(0,0)):
        self.string = string
        self.position = position
        self.text = Text(string, position)
        self.value = value
    
    def keymenu(self, screen):
        keymenu = KeyMenu(self.string, screen, self.value)
        self.value = keymenu.mainloop()
    
    def print_me(self, screen):
        if self.position != self.text.position:
            self.text.position = self.position
        self.text.print_me(screen)


class CharMenu():
    def __init__(self, list, cursor, orientation=True):
        self.list = list
        self.orientation = orientation
        self.mugs_start = 0
        self.cursor_pos = 0
        self.lock=False
        if orientation:
            self.cursor = cursor[0]
        else: self.cursor = cursor[1]
        self.arrow_left = cursor[2]
        self.arrow_right = cursor[3]
        self.cursor_tick = 0
        self.cursor_frame = 0
        self.alt = False
        self.update()
        self.surface = pygame.Surface((160, 240)).convert_alpha()
        self.flash = False
        self.flash_int = 0
    
    def ready(self):
        return self.lock and self.flash_int == 0
    
    def return_me(self):
        return (self.list[self.mugs_start+self.cursor_pos], self.alt)
    
    def print_me(self, screen):
        # print portrait
        if self.orientation:
            screen.blit(self.portrait, (22,22))
        else:
            screen.blit(pygame.transform.flip(self.portrait, 1,0), (200,22))
        
        # print name
        self.text.print_me(screen)
        
        # print mugs
        if self.orientation:
            if self.mug1 != None:
                screen.blit(self.mug1, (15,160))
            if self.mug2 != None:
                screen.blit(self.mug2, (46,160))
            if self.mug3 != None:
                screen.blit(self.mug3, (77,160))
            if self.mug4 != None:
                screen.blit(self.mug4, (108,160))
        else:
            if self.mug1 != None:
                screen.blit(self.mug1, (175,160))
            if self.mug2 != None:
                screen.blit(self.mug2, (206,160))
            if self.mug3 != None:
                screen.blit(self.mug3, (237,160))
            if self.mug4 != None:
                screen.blit(self.mug4, (268,160))
        
        # print arrows
        length = len(self.list)
        if length > 4 and not self.lock:
            if self.orientation:
                if self.mugs_start > 1:
                    screen.blit(self.arrow_right[self.cursor_frame],(-3,150))
                if self.mugs_start < length-4:
                    screen.blit(self.arrow_left[self.cursor_frame],(123,150))
            else:
                if self.mugs_start > 1:
                    screen.blit(self.arrow_right[self.cursor_frame],(157,150))
                if self.mugs_start < length-4:
                    screen.blit(self.arrow_left[self.cursor_frame],(283,150))
        
        # print cursor
        if not self.lock:
            if self.orientation:
                screen.blit(self.cursor[self.cursor_frame], (13+(self.cursor_pos*31),150))
            else: screen.blit(self.cursor[self.cursor_frame], (173+(self.cursor_pos*31),150))
            self.cursor_tick +=1
            if self.cursor_tick > 2:
                self.cursor_tick = 0
                self.cursor_frame += 1
                if self.cursor_frame > 3:
                    self.cursor_frame = 0
        
        if self.flash_int != 0:
            color = (255,255,255, self.flash_int)
            self.surface.fill(color)
            if self.orientation:
                screen.blit(self.surface, (0,0))
            else: screen.blit(self.surface, (160,0))
            if self.flash:
                self.flash_int -= 50
                if self.flash_int < 0:
                    self.flash_int = 0
                    self.flash = False
            else:
                self.flash_int += 50
                if self.flash_int > 255:
                    self.flash_int = 255
                    self.flash = True
                
    def getmugvar(self):
        if self.choice == 0:
            return 1
        elif self.choice == len(self.list)-1:
            return -2
        elif self.choice == len(self.list)-2:
            return -1
        else: return 0
        
    def update(self):
        self.portrait = pygame.image.load('../res/Char/'+self.list[self.mugs_start+self.cursor_pos]+'/portrait.png').convert_alpha()
        
        length = len(self.list)
        self.mug1 = pygame.image.load('../res/Char/'+self.list[self.mugs_start]+'/mug.png').convert_alpha()
        if self.mugs_start+1 < length:
            self.mug2 = pygame.image.load('../res/Char/'+self.list[self.mugs_start+1]+'/mug.png').convert_alpha()
        else: self.mug2 = None
        if self.mugs_start+2 < length:
            self.mug3 = pygame.image.load('../res/Char/'+self.list[self.mugs_start+2]+'/mug.png').convert_alpha()
        else: self.mug3 = None
        if self.mugs_start+3 < length:
            self.mug4 = pygame.image.load('../res/Char/'+self.list[self.mugs_start+3]+'/mug.png').convert_alpha()
        else: self.mug4 = None
        
        if self.orientation:
            point = Point(20,130)
        else: point = Point(205,130)
        
        self.text = Text(self.list[self.mugs_start+self.cursor_pos], point)
    
    def left(self):
        if self.lock:
            return
        config.SoundPlayer().play_sound('menumove.wav')
        self.cursor_pos -= 1
        if self.cursor_pos < 1 and self.mugs_start > 0:
            self.cursor_pos += 1
            self.mugs_start -=1
        if self.cursor_pos < 0:
            self.cursor_pos = 0
        self.update()
        
    def right(self):
        if self.lock:
            return
        config.SoundPlayer().play_sound('menumove.wav')
        num = len(self.list)
        self.cursor_pos += 1
        if self.cursor_pos > 2 and self.mugs_start < num-4:
            self.cursor_pos -= 1
            self.mugs_start +=1
        if self.cursor_pos > 3:
            self.cursor_pos = 3
        if self.cursor_pos > num-1:
            self.cursor_pos = num-1
        self.update()
    
    def select(self):
        if not self.lock:
            self.lock = True
            self.flash_int = 5
            self.alt=False
            config.SoundPlayer().play_sound('menuok.wav')
            
    def cancel(self):
        if self.lock:
            self.lock = False
            config.SoundPlayer().play_sound('menucancel.wav')
            
    def special(self):
        if not self.lock:
            self.lock = True
            self.flash_int = 5
            self.alt=True
            config.SoundPlayer().play_sound('menuok.wav')

class CharSelectMenu(Menu):
    def __init__(self, screen, KeysP1, KeysP2, position = Point(0,0)):
        Menu.__init__(self, position, screen)
        charlist = getCharList()
        self.keysP1 = KeysP1
        self.keysP2 = KeysP2
        self.cursor_sprites = game.GameObject('../res/charcursor.png', 36, 44, Point(0,0)).sprite_list
        self.charmenuP1 = CharMenu(charlist, self.cursor_sprites, True)
        self.charmenuP2 = CharMenu(charlist, self.cursor_sprites, False)
    
    def mainloop(self):
        background = pygame.image.load('../res/Background/SelectScreen.png').convert()
        clock = pygame.time.Clock()
        
        while True:
            
            if self.charmenuP1.ready() and self.charmenuP2.ready():
                return (self.charmenuP1.return_me(), self.charmenuP2.return_me())
            
            ## Conditions d'arret du programme
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return 0
                    if event.key == self.keysP1[2]:
                        self.charmenuP1.left()
                    if event.key == self.keysP1[3]:
                        self.charmenuP1.right()
                    if event.key == self.keysP1[4]:
                        self.charmenuP1.select()
                    if event.key == self.keysP1[5]:
                        self.charmenuP1.cancel()
                    if event.key == self.keysP1[6]:
                        self.charmenuP1.special()
                    
                    if event.key == self.keysP2[2]:
                        self.charmenuP2.left()
                    if event.key == self.keysP2[3]:
                        self.charmenuP2.right()
                    if event.key == self.keysP2[4]:
                        self.charmenuP2.select()
                    if event.key == self.keysP2[5]:
                        self.charmenuP2.cancel()
                    if event.key == self.keysP2[6]:
                        self.charmenuP2.special()
            
            ## Rafraichissement de l'ecran
            self.screen.fill((0,0,0))
            ## BG
            self.screen.blit(background, (0,0))
            self.charmenuP1.print_me(self.screen)
            self.charmenuP2.print_me(self.screen)
            
            clock.tick(30)
            
            config.Screen().display_update(self.screen)

class Credits():
    def __init__(self, screen, position = Point(0,0)):
        self.screen = screen
        self.position = position
        self.texts=[]
        self.addTxt('')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('A game by Saitho')
        self.addTxt('  comment on:')
        self.addTxt('    pygame.org')
        self.addTxt('')
        self.addTxt('sprites from:')
        self.addTxt('The sprite database')
        self.addTxt('  sdb.drshnaps.com')
        self.addTxt('')
        self.addTxt('ripped by:')
        self.addTxt('  Grim')
        self.addTxt('  DARKR')
        self.addTxt('  FMit')
        self.addTxt('')
        self.addTxt('Sounds ripped by:')
        self.addTxt('  Don Camilo')
        self.addTxt('  HelpTheWretched')
        self.addTxt('')
        self.addTxt('Musics from:')
        self.addTxt('Sounds 4 RPG Maker:')
        self.addTxt('  Dungeons & Fields')
        self.addTxt('by:  Flane Boster')
        self.addTxt('')
        self.addTxt('A big thanks to')
        self.addTxt('  Fred')
        self.addTxt('  Olivier')
        self.addTxt('  Martin')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('')
        self.addTxt('  and thank you')
        self.addTxt('  for playing !!')
        self.addTxt('')
    
    def addTxt(self, string):
        self.texts.append(Text(string, Point(10,10+16*len(self.texts))))
    
    def move(self):
        for text in self.texts:
            text.position += (0,-1)
    
    def rotate(self):
        string = self.texts[0].string
        self.texts.pop(0)
        self.addTxt(string)
    
    def mainloop(self):
        background = pygame.image.load('../res/Background/OptionScreen.png').convert()
        clock = pygame.time.Clock()
        self.tick = 0
        
        while True:
            ## Conditions d'arret du programme
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                if event.type == KEYDOWN:
                    config.SoundPlayer().play_sound('menucancel.wav')
                    return 0
            
            clock.tick(30)
            self.move()
            if self.texts[1].position.y < -16:
                self.rotate()
            
            ## Rafraichissement de l'ecran
            self.screen.fill((0,0,0))
            ## BG
            self.screen.blit(background, (0,0))
            for text in self.texts:
                text.print_me(self.screen)
            
            config.Screen().display_update(self.screen)

class StatsMenu:
    def __init__(self, screen, fight_stats, position = Point(0,0)):
        self.screen = screen
        self.texts_P1=[]
        self.texts_P2=[]
        self.keysP1 = config.OptionConfig().keysP1
        self.keysP2 = config.OptionConfig().keysP2
        
        win_perc_P1 = round(fight_stats.wins_P1/(fight_stats.wins_P1+fight_stats.wins_P2) * 100)
        rounds_perc_P1 = round(fight_stats.rounds_P1/(fight_stats.rounds_P1+fight_stats.rounds_P2) * 100)
        win_perc_P2 = round(fight_stats.wins_P2/(fight_stats.wins_P1+fight_stats.wins_P2) * 100)
        rounds_perc_P2 = round(fight_stats.rounds_P2/(fight_stats.rounds_P1+fight_stats.rounds_P2) * 100)
        
        draw_perc = round(fight_stats.draws/(fight_stats.wins_P1+fight_stats.wins_P2+fight_stats.draws) * 100)
        
        if fight_stats.lastwin != 0:
            self.addTxt(self.texts_P1, "Player "+str(fight_stats.lastwin)+" wins !")
        else:
            self.addTxt(self.texts_P1, "Draw game !!")
        self.addTxt(self.texts_P1)
        self.addTxt(self.texts_P1, "Stats")
        
        self.addTxt(self.texts_P1, "P1:")
        self.addTxt(self.texts_P1, str(fight_stats.wins_P1)+" win(s)")
        self.addTxt(self.texts_P1, "("+str(win_perc_P1)+"%)")
        self.addTxt(self.texts_P1, str(fight_stats.rounds_P1)+" round(s)")
        self.addTxt(self.texts_P1, "("+str(rounds_perc_P1)+"%)")
        self.addTxt(self.texts_P1)
        self.addTxt(self.texts_P1, "Draws:"+str(fight_stats.draws)+"("+str(draw_perc)+"%)")
        
        self.addTxt(self.texts_P2)
        self.addTxt(self.texts_P2)
        self.addTxt(self.texts_P2)
        self.addTxt(self.texts_P2, "P2:")
        self.addTxt(self.texts_P2, str(fight_stats.wins_P2)+" win(s)")
        self.addTxt(self.texts_P2, "("+str(win_perc_P2)+"%)")
        self.addTxt(self.texts_P2, str(fight_stats.rounds_P2)+" round(s)")
        self.addTxt(self.texts_P2, "("+str(rounds_perc_P2)+"%)")
        
        self.select = MultChoice("Select", ["rematch","char. select","main menu"], 0, Point(0,200))
        
    
    def addTxt(self, textlist, string=""):
        textlist.append(Text(string, Point(10,10+16*len(textlist))))
    
    def mainloop(self):
        background = pygame.image.load('../res/Background/OptionScreen.png').convert()
        clock = pygame.time.Clock()
        self.tick = 0
        
        while True:
            ## Conditions d'arret du programme
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                if event.type == KEYDOWN:
                    if event.key == self.keysP1[2] \
                    or event.key == self.keysP2[2]:
                        self.select.more()
                    if event.key == self.keysP1[3] \
                    or event.key == self.keysP2[3]:
                        self.select.less()
                    if event.key == self.keysP1[4] \
                    or event.key == self.keysP1[5] \
                    or event.key == self.keysP1[6] \
                    or event.key == self.keysP2[4] \
                    or event.key == self.keysP2[5] \
                    or event.key == self.keysP2[6]:
                        return self.select.choice
            
            clock.tick(30)
            
            ## Rafraichissement de l'ecran
            self.screen.fill((0,0,0))
            ## BG
            self.screen.blit(background, (0,0))
            for text in self.texts_P1:
                text.print_me(self.screen)
            for text in self.texts_P2:
                text.print_me(self.screen, Point(160,0))
            self.select.print_me(self.screen)
            
            config.Screen().display_update(self.screen)

class OptionMenu(Menu):
    def __init__(self, screen, position = Point(0,0)):
        self.config = config.OptionConfig('../res/config.txt')
        Menu.__init__(self, position, screen, 'OptionScreen.png')
        self.addElt(Text('Game Options'))
        self.addElt(MultChoice('Time', ['infinite', '30', '60', '99'], value = self.config.time))
        self.addElt(MultChoice('Rounds to win', ['1', '2', '3', '5'], value = self.config.rounds))
        self.addElt(Text(''))
        self.addElt(Text('Video Option:'))
        self.addElt(MultChoice('Size', ['320x240', '640x480', '640x480(2X)', '800x600', '960x720', '960x720(2X)', '1280x960', '1280x960(2X)', 'Fullscreen'], value = self.config.video))
#        self.addElt(YesNo('Fullscreen', value = self.config.fullscreen))
        self.addElt(Text(''))
        self.addElt(Text('Sound Options'))
        self.addElt(Value('Sound', value = self.config.sound, maxValue = 8))
        self.addElt(Value('Music', value = self.config.music, maxValue = 8))
        self.addElt(Text(''))
        self.addElt(KeySetter('Set keys for P1', value = self.config.keysP1))
        self.addElt(KeySetter('Set keys for P2', value = self.config.keysP2))
        self.choice = 1
    
    def back(self):
        self.config.time = self.options[1].choice
        self.config.rounds = self.options[2].choice
        self.config.video = self.options[5].choice
        self.config.sound = self.options[8].value
        self.config.music = self.options[9].value
        self.config.keysP1 = self.options[11].value
        self.config.keysP2 = self.options[12].value
        self.config.saveconfig('../res/config.txt')

class MainMenu(Menu):
    def __init__(self, screen, position = Point(0,0)):
        self.config = config.OptionConfig('../res/config.txt')
        config.SoundPlayer().play_music('Intro.mp3')
        Menu.__init__(self, position, screen, 'MenuScreen.png')
        self.addElt(MenuElt('Start Vs Game', self.call_game))
        self.addElt(MenuElt('Options', self.call_option))
        self.addElt(MenuElt('Credits', self.call_credits))
        self.choice = 0
        self.fight_stats = Fight_stats()
    
    def call_option(self):
        menu = OptionMenu(self.screen, Point(20,10))
        menu.mainloop()
    
    def call_game(self):
        self.choice = 0
        self.fight_stats = Fight_stats() # Reinit stats
        while True:
            char1, char2 = self.call_charmenu()
            if char1 == 0 and char2 == 0:
                break
            while True:
                if self.call_fight(char1, char2):
                    self.choice = self.call_fight_stats()
                    char1.reinit_energy()
                    char2.reinit_energy()
                else:
                    self.choice = 2
                if self.choice > 0:
                    break
            if self.choice > 1:
                break
        self.choice = 0
                    
    def call_charmenu(self):
        self.config = config.OptionConfig()
        menu = CharSelectMenu(self.screen, self.config.keysP1, self.config.keysP2, Point(0,0))
        characters = menu.mainloop()
        if characters == 0:
            return 0, 0
        char1 = characters[0][0]
        alt1 = characters[0][1]
        char2 = characters[1][0]
        alt2 = characters[1][1]
        if char1 == char2 and alt1 == alt2:
            alt2 = not alt1
        print('loading characters...')
        player1 = Round.Player(char1, 120, 100, alt_color = alt1)
        player2 = Round.Player(char2, 120, 100, Player2=True, alt_color = alt2)
        return player1, player2
    
    def call_fight(self, player1, player2):
        print('loading background...')
        list = getBckgrndList()
        rand = randint(0, len(list)-1)
        background = Round.Background('../res/Background/'+list[rand])
        config.SoundPlayer().play_music('Bckgrnd3.mp3')
        print('creating game...')
        game = Round.Game(self.screen, background, player1, player2)
        results = game.mainloop()
        config.SoundPlayer().play_music('Intro.mp3')
        if results == 'QUIT':
            return False
        else:
            self.fight_stats.update(results)
            return True
    
    def call_fight_stats(self):
        stats_menu = StatsMenu(self.screen, self.fight_stats)
        return stats_menu.mainloop()
    
    def call_credits(self):
        menu = Credits(self.screen, Point(20,20))
        menu.mainloop()
    
    def back(self):
        print('quit')
        exit()

if __name__ == "__main__":
    
    pygame.init()
    screen = pygame.display.set_mode((320, 240), 0, 32)
    pygame.display.set_caption("MenuTest") # program title
    menu = OptionMenu(screen, Point(20,10))
    menu.mainloop()