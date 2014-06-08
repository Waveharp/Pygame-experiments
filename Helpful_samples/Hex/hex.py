## Francisco Rivera - franr.com.ar/hex |
## ------------------------------------/

# import os
import random
from threading import Thread
import pygame

# constantes
RUN = True
LONG = 20
AMARILLO = (255, 231, 0)
AMARILLO_C = (255, 255, 50)
AZUL = (0, 127, 245)
AZUL_C = (50, 177, 255)
BLANCO = (255,255,255)
NEGRO = (0,0,0)
color_jugador_claro = AZUL_C
jugador = AZUL

def cambiar_jugador():
    global jugador
    global color_jugador_claro
    
    if jugador == AZUL:
        jugador = AMARILLO
        color_jugador_claro = AMARILLO_C
    else:
        jugador = AZUL
        color_jugador_claro = AZUL_C
        

class Fuente:

    def __init__(self):
        pygame.font.init()
        self.fuente = pygame.font.Font("cubicfive10.ttf", 20)

    def render(self, texto):
        return self.fuente.render(texto, False, NEGRO)


class Hexagono:

    def __init__(self, pantalla, x, y, id, azul_p, azul_f, amarillo_p, amarillo_f):
        self.pantalla = pantalla
        self.d = LONG
        self.color = BLANCO
        self.marcada = False
        self.id = id
        self.azul_p = azul_p
        self.azul_f = azul_f
        self.amarillo_p = amarillo_p
        self.amarillo_f = amarillo_f
        # coordenadas del centro
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x - self.d/2 - 4, self.y - self.d, self.d + 8, self.d*2)

    def dibujar(self):
        pl = [(self.x - self.d, self.y),
              (self.x - self.d/2, self.y - self.d),
              (self.x + self.d/2, self.y - self.d),
              (self.x + self.d, self.y),
              (self.x + self.d/2, self.y + self.d),
              (self.x - self.d/2, self.y + self.d)]
        pygame.draw.polygon(self.pantalla, self.color, pl)
        pygame.draw.polygon(self.pantalla, (100,100,100), pl, 3)
        # pygame.draw.rect(self.pantalla, NEGRO, self.rect)

    def update(self, x, y, p):
        c = self.rect.collidepoint(x, y)
        if c:
            if p and self.color == color_jugador_claro:
                self.marcar()
                cambiar_jugador()
                return 1
            return 2
        return 0
        
    def marcar(self):
        self.color = jugador
        self.marcada = True
            
    def enfocar(self):
        if not self.marcada:
            self.color = color_jugador_claro
        
    def desenfocar(self):
        if not self.marcada:
            self.color = BLANCO


class Tablero:

    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.iniciar()
        
    def iniciar(self):
        self.hexas = {}
        self.foco = None
        self.id = 0
        dx = LONG
        dy = LONG*11
        # tablero
        for i in range(11):
            for e in range(11):
                x = dx + LONG*(e + i)*1.5
                y = dy + LONG*(i - e)
                self.id += 1
                azp, azf, amp, amf = self.borde(self.id)
                self.hexas[self.id] = Hexagono(self.pantalla, x, y, self.id, azp, azf, amp, amf)
                
    def borde(self, id):
        # esquina <
        if id == 1:
            return True, False, True, False
        # esquina ^
        elif id == 11:
            return False, True, True, False
        # esquina V
        elif id == 111:
            return True, False, True, False
        # esquina >
        elif id == 121:
            return False, True, False, True
        # borde <V azul_p
        elif id % 11 == 1:
            return True, False, False, False
        # borde <^ amarillo_p
        elif id > 1 and id < 11:
            return False, False, True, False
        # borde ^> azul_f        
        elif (id % 11) == 0:
            return False, True, False, False
        # borde ^> amarillo_f
        elif (id - 110) > 1 and (id - 110) < 11:
            return False, False, False, True
        # medio
        else:
            return False, False, False, False

    def dibujar(self):
        pygame.draw.rect(self.pantalla, AMARILLO, (0, 0, LONG*11*1.5, LONG*11))
        pygame.draw.rect(self.pantalla, AZUL, (LONG*11*1.5, 0, LONG*11*1.5*2, LONG*11))
        pygame.draw.rect(self.pantalla, AZUL, (0, LONG*11, LONG*11*1.5, LONG*11))
        pygame.draw.rect(self.pantalla, AMARILLO, (LONG*11*1.5, LONG*11, LONG*11*1.5, LONG*11))        
        x, y = pygame.mouse.get_pos()        
        click = pygame.event.wait().type == pygame.MOUSEBUTTONDOWN
        gano = None
        for h in self.hexas.values():
            r = h.update(x, y, click)
            if r:
                # marco
                if r == 1:
                    self.foco = None
                    gano = self.resolver(h.id)
                # enfoco
                elif r == 2:
                    if self.foco and self.foco != h:
                        self.foco.desenfocar()
                    self.foco = h
            if self.foco:
                self.foco.enfocar()
            h.dibujar()
        return gano
            
    def resolver(self, id):
        vistos = []
        color = self.hexas[id].color
        cadena = [h for h in self.alrededor(id, color, vistos)]
        if self.principio(cadena, color) and self.fin(cadena, color):
            return color
        return None
        
    def alrededor(self, id, color, vistos):
        # devuelve los ids de los hexagonos del mismo color alrededor de uno
        if self.borde(id)[0] == True:
            pos = 0, -10, -11, 1, 11
        elif self.borde(id)[1] == True:
            pos = 0, -11, -1, 11, 10
        else:
            pos = 0, -10, -11, 1, -1, 11, 10
        alr = [self.hexas[id+i].id for i in pos if (self.hexas.has_key(id+i) and (id+i not in vistos))]
        cadena = [self.hexas[h].id for h in alr if (self.hexas[h].color == color)]
        vistos.extend(cadena)
        for i in cadena:
            self.alrededor(i, color, vistos)
        return vistos

    def principio(self, cadena, color):
        if color == AZUL:
            for c in cadena:
                if self.hexas[c].azul_p:
                    return True
        else:
            for c in cadena:
                if self.hexas[c].amarillo_p:
                    return True            
        return False
    
    def fin(self, cadena, color):
        if color == AZUL:
            for c in cadena:
                if self.hexas[c].azul_f:
                    return True
        else:
            for c in cadena:
                if self.hexas[c].amarillo_f:
                    return True            
        return False
    

class Pantalla:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hex")
        self.clock = pygame.time.Clock()
        # os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.pantalla = pygame.display.set_mode((LONG*32, LONG*11*2))
        self.t = Tablero(self.pantalla)
        self.gano = True
        self.color = None
        self.fuente = Fuente()
        self.main()        

    def main(self):
        global RUN
        while RUN:
            self.pantalla.fill(AZUL_C)
            # mostramos            
            pygame.event.pump()
            if not self.gano:
                color = self.t.dibujar()
                if color:
                    self.gano = True
                    self.color = color
            else:
                self.ganador()
            pygame.display.update()
            if not self.update():
                RUN = False
                break
            self.clock.tick(40)
        pygame.quit()
        
    def ganador(self):
        if self.color == AZUL:
            color = "Azul"
        else:
            color = "Amarillo"

        if self.color:
            r1 = self.fuente.render("Gano el jugador " + color)
        r2 = self.fuente.render("[i] Iniciar")
        r3 = self.fuente.render("[Esc] Salir")
        r4 = self.fuente.render("franr.com.ar/hex")
        
        if self.color:
            self.pantalla.blit(r1, (200,50))
        self.pantalla.blit(r2, (200,200))
        self.pantalla.blit(r3, (200,250))
        self.pantalla.blit(r4, (370,410))

    def update(self):
        k = pygame.key.get_pressed()
        if k[pygame.K_ESCAPE]:
            return False
        elif k[pygame.K_i]:
            self.gano = False
            self.t.iniciar()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
        return True

Pantalla()