##############################################################################
# systemevents.py
##############################################################################
# Definitions of all system events monitored by the game engine's main
# event manager.
##############################################################################
# 06/12 - Flembobs
##############################################################################

from events import *
from weakref import WeakKeyDictionary 

##############################################################################
# EVENTS
##############################################################################

class TickEvent(Event):
   """
   Generated by the CPU Spinner when a game loop occurs
   """
   pass
   
class QuitEvent(Event):
   """
   Generated by the model when the user tries to quit the game.
   """
   pass
   
class KeyboardEvent(Event):
   """
   Generated by the pygame event monitor when the user presses or releases a 
   key.
   """   
   
   def __init__(self,type,key):
      """
      type - pygame.KEYUP or pygame.KEYDOWN
      key - which key e.g. pygame.K_ESCAPE
      """ 
      
      self.type = type
      self.key = key
      
class MouseButtonEvent(Event):
   """
   Generated by the pygame event monitor when the user presses or releases
   a mouse button.
   """
   
   def __init__(self,type,button,pos):
      """
      type - pygame.MOUSEBUTTONUP or pygame.MOUSEBUTTONDOWN
      button - which mouse button was pressed
      pos - position of the mouse at time of event
      """
      
      self.type = type                            
      self.button = button
      self.pos = pos
      
class MouseMotionEvent(Event):
   """
   Generated by the pygame event monitor when the user moves the mouse.
   """
   
   def __init__(self,pos,rel,buttons):
      """
      pos - new position of the mouse
      rel - position relative to the old position
      buttons - which buttons are being pressed
      """
            
      self.pos = pos
      self.rel = rel
      self.buttons = buttons
      
class DrawRequestEvent(Event):
   """
   Generated by the model when it wants to be drawn.
   """
   
   def __init__(self,visible_objects):
      """
      visible_objects - Game objects that are to be drawn on screen.
                        They will be drawn in the order they appear in this
                        list.
      """
   
      self.visible_objects = visible_objects

##############################################################################
# LISTENER
##############################################################################

class SystemEventListener(Listener):
   
   def __init__(self):
      """
      Creates a System Event Listener that will register itself with the
      System Event Manager.
      """
      Listener.__init__(self,SystemEventManager)

##############################################################################
# EVENTS MANAGER
##############################################################################

class SystemEventManager(EventManager):
   listeners = WeakKeyDictionary()