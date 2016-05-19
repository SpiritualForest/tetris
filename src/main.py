# System-wide imports
import curses
import select
import sys
# Local (personal) imports
import window
import game
import debug
import ai

# FIXME: Pause the automatic drop when the player presses down, restart it when the player doesn't move the object downwards.

# init colour pairs
def initpairs():
    # Initialize the curses colour pairs. Yes, I know this tuple is ugly.
    colours = (curses.COLOR_GREEN, curses.COLOR_BLUE,
                curses.COLOR_RED, curses.COLOR_MAGENTA, curses.COLOR_YELLOW,
                curses.COLOR_CYAN, curses.COLOR_WHITE)
    for i, colour in enumerate(colours):
        curses.init_pair(i + 1, colour, colour)
    # Now the menu colour pair.
    curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_BLACK)

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
    while not win.handleInput():
        # if handleInput() returned False, we continue to loop,
        continue
    win.window.clear()
    return win.choice 

def main():
    # Initialize curses
    stdscr = initCurses()
    initpairs()
    gameinprogress = False # There can be more than one game running simultaneously.
    gObjects = {} # Game objects
    finishedGame = None # Used for removing a game from the gObjects dict
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
                gameObject = game.Game(stdscr, False) # True for human, False for AI player
                gameObject.gamerunning = 1
                gObjects[gameObject] = True
                gameinprogress = True
                gameObject.aiObject = ai.AI(gameObject.windowObject)
            elif gametype == game.GT_AIVSAI:
                # AI vs AI.
                pass
            elif gametype == game.GT_HVSAI:
                # Human vs AI.
                pass
            else:
                # Fifth option. Clear the screen and quit by exiting the loop.
                stdscr.clear()
                break
        else:
            # There is a game (or games) in progress.
            for gameObj in gObjects:
                if gameObj.gamerunning:
                    gameObj.run()
                else:
                    finishedGame = gameObj
            if finishedGame:
                gObjects.pop(finishedGame)
                finishedGame = None
            if not gObjects:
                # All games are done. Display the menu again.
                stdscr.clear()
                gameinprogress = False

if __name__ == "__main__":
    main()
    debug.end()
    curses.endwin()
