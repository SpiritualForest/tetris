# System-wide imports
import curses
import select
import sys
# Local (personal) imports
import window
import game
import debug

# TODO: Completely refactor the main loop, and clean up code.
# FIXME: Pause the automatic drop when the player presses down, restart it when the player doesn't move the object downwards.

# init colour pairs
def initpairs():
    # Initialize the curses colour pairs. Yes, I know this tuple is ugly.
    colours = (curses.COLOR_GREEN, curses.COLOR_BLUE,
                curses.COLOR_RED, curses.COLOR_MAGENTA, curses.COLOR_YELLOW,
                curses.COLOR_CYAN, curses.COLOR_WHITE)
    for i, colour in enumerate(colours):
        curses.init_pair(i + 1, colour, colour)

def initCurses():
    stdscr = curses.initscr()
    stdscr.keypad(True)
    stdscr.immedok(True) # This setting causes an immediate refresh() to be called on each change
    curses.noecho()
    curses.cbreak()
    curses.nonl()
    curses.start_color()
    try:
        # Make the cursor invisible. Continue anyway if impossible.
        curses.curs_set(0)
    except curses.error:
        pass
    # Return the stdscr window object
    return stdscr

def menu(maxyx):
    # Displays the menu of game choices
    win = window.MenuWindow(maxyx)
    choice = win.handleInput()
    while not choice:
        # if handleInput() returned False, we continue to loop,
        choice = win.handleInput()
    win.window.clear()
    return win.choice 

def main():
    # Initialize curses and get the window object
    stdscr = initCurses()
    initpairs()
    gameinprogress = False
    gObjects = {} # Game objects
    gamedoneObj = None # Used for removing a game from the gObjects dict
    while 1:
        # If there is no game in progress, display the options menu.
        # Otherwise, the game runs.
        if not gameinprogress:
            gametype = menu(stdscr.getmaxyx())
            if gametype == game.GT_SINGLE:
                # Single player game
                gameObject = game.Game(stdscr)
                gameObject.gamerunning = 1
                gObjects[gameObject] = True
                gameinprogress = True
            elif gametype == game.GT_AI:
                # Watch AI.
                pass
            elif gametype == game.GT_AIVSAI:
                # AI vs AI.
                pass
            elif gametype == game.GT_HVSAI:
                # Human vs AI.
                pass
            else:
                # Fifth option. Quit by exiting the loop.
                break
        else:
            # There is a game (or games) in progress.
            for gameObj in gObjects:
                if gameObj.gamerunning:
                    gameObj.run()
                else:
                    gamedoneObj = gameObj
            if gamedoneObj:
                gObjects.pop(gamedoneObj)
                gamedoneObj = None
            if not gObjects:
                # All games are done. Display the menu again.
                gameinprogress = False

if __name__ == "__main__":
    main()
    debug.end()
    curses.endwin()
