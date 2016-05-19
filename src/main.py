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
        debug.debug("The value of choice is: %s" % choice)
    win.window.clear()
    return win.choice    

def main():
    # Initialize curses and get the window object
    stdscr = initCurses()
    initpairs()
    # Display the menu.
    gametype = menu(stdscr.getmaxyx())
    if gametype == game.GT_SINGLE:
        # Single player game
        gameObject = game.Game(stdscr)
        gameObject.gamerunning = 1
        while gameObject.gamerunning:
            gameObject.run()
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
        # Fifth option. Quit.
        debug.end()
        curses.endwin()

if __name__ == "__main__":
    main()
