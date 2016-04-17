# System-wide imports
import curses
import select
import time
import sys
# Local (personal) imports
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
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    try:
        # Make the cursor invisible. Continue anyway if impossible.
        curses.curs_set(0)
    except curses.error:
        pass
    # Return the stdscr window object
    return stdscr

def main():
    # Initialize curses and get the window object
    stdscr = initCurses()
    initpairs()
    # Create a game object and start the game
    gameObject = game.Game(stdscr)
    gameObject.gamerunning = 1
    interval = int(time.time()) + 1
    windowObject = gameObject.windowObject
    while gameObject.gamerunning:
        if not gameObject.hasblock():
            if windowObject.starty + 1 in windowObject.grid:
                # Top line reached. Cannot spawn object. Game must end.
                gameObject.gamerunning = 0
                return
            blockObj = gameObject.spawnBlock()
            gameObject.setBlock(blockObj(windowObject.rangey, windowObject.rangex))
        else:
            windowObject.draw(gameObject.blockObj.coordinates, gameObject.blockObj.colour)
            r, o, e = select.select([sys.stdin], [], [], 0.01)
            mwp = gameObject.handleInput(r) # method with params
            if mwp is None:
                # No command found
                continue
            if len(mwp) > 1:
                method, params = mwp
                method(params)
            else:
                method = mwp[0]
                method()
        
    curses.endwin()

if __name__ == "__main__":
    main()
    debug.end()
