# System import
import curses
import random
import select
import time
import sys
# Local import
import game
import debug
        
# init colour pairs

def initpairs():
    # Initialize the curses colour pairs. Yes, I know this tuple is ugly.
    colours = (curses.COLOR_GREEN, curses.COLOR_BLUE,
                curses.COLOR_RED, curses.COLOR_MAGENTA, curses.COLOR_YELLOW,
                curses.COLOR_CYAN, curses.COLOR_WHITE)
    for i, colour in enumerate(colours):
        curses.init_pair(i + 1, colour, colour)

def main():
    stdscr = curses.initscr()
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    try:
        # Make the cursor invisible. Continue anyway if impossible
        curses.curs_set(0)
    except curses.error:
        pass
    # Start colour and initialize pairs
    curses.start_color()
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
            windowrangey = (windowObject.starty, windowObject.endy)
            windowrangex = (windowObject.startx, windowObject.endx)
            blockObj = gameObject.spawnBlock()
            gameObject.setBlock(blockObj(windowrangey, windowrangex))
        else:
            windowObject.draw(gameObject.blockObj.coordinates, gameObject.blockObj.colour)
            r, o, e = select.select([sys.stdin], [], [], 0.01)
            currenttime = int(time.time())
            if currenttime == interval:
                gameObject.movementOrigin = game.O_GAME
                gameObject.move(curses.KEY_DOWN)
                interval = currenttime + gameObject.interval
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
