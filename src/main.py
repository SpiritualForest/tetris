# System-wide imports
import curses
import select
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
    stdscr.immedok(True) # This setting causes an immediate refresh() to be called on each change
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
    while gameObject.gamerunning:
        if not gameObject.blockObj:
            # Spawn a block.
            b = gameObject.spawnBlock()
            gw = gameObject.windowObject.window # Game window
            blockObj = b(gw.rangey, gw.rangex)
            nbobj = b(gameObject.nbw.window.rangey, gameObject.nbw.window.rangex)
            gameObject.setBlock(blockObj)
            gameObject.nbw.window.clear()
            gameObject.nbw.window.draw(nbobj.coordinates, nbobj.colour)
        else:
            gameObject.windowObject.window.draw(blockObj.coordinates, blockObj.colour)
            gameObject.automove()
            r, o, e = select.select([sys.stdin], [], [], 0.01)
            mwp = gameObject.handleInput(r)
            if mwp:
                method = mwp[0]
                try:
                    params = mwp[1]
                    method(params)
                except IndexError:
                    method()

if __name__ == "__main__":
    main()
    debug.end()
    curses.endwin()
