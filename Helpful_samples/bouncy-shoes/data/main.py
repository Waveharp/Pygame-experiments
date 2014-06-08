from data.states import main_menu
from data.states import level
from data.states import controls
from data.states import livesleft
from data.states import gameover
from . import setup, tools

MAIN_MENU = 'main menu'
LEVEL1 = 'level1'
CONTROLS = 'controls'
LIVES_LEFT = 'lives left'
GAME_OVER = 'game over'

def main():
    """
    Add states to control here.
    """
    run_it = tools.Control(setup.ORIGINAL_CAPTION)
    state_dict = {MAIN_MENU: main_menu.Menu(),
                  LEVEL1: level.Level(LEVEL1),
                  CONTROLS: controls.Controls(),
                  LIVES_LEFT: livesleft.LivesLeft(),
                  GAME_OVER: gameover.GameOver()

                  }

    run_it.setup_states(state_dict, MAIN_MENU)
    run_it.main()

