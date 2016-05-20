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

def createGame(stdscr, *types):
    # Creates games objects based on the types passed in the <types> argument
    # GT_SINGLE refers to a human player.
    games = []
    gameObject = None
    for gtype in types:
        if gtype not in (game.GT_SINGLE, game.GT_AI):
            # Not a game type.
            return
        if gtype == game.GT_SINGLE:
            # Human player
            gameObject = game.Game(stdscr, human=True)
        else:
            # AI game. Pass False to indicate it's not a human-controlled game.
            # Also create an AI object and set it.
            gameObject = game.Game(stdscr, human=False)
            gameObject.aiObject = ai.AI(gameObject.windowObject)
        # Run the game and append it to the running games list.
        gameObject.gamerunning = True
        games.append(gameObject)
    # Return the resulting list.
    return games

def main():
    # Initialize curses
    stdscr = initCurses()
    initpairs()
    gameinprogress = False # There can be more than one game running simultaneously.
    games = []
    finishedGame = None # Used for removing a game from the gObjects dict
    while 1:
        # If there is no game in progress, display the options menu.
        # Otherwise, the game runs.
        if not gameinprogress:
            gametype = menu(stdscr.getmaxyx())
            if gametype == game.GT_SINGLE:
                # Single player game
                games.extend(createGame(stdscr, game.GT_SINGLE))
                gameinprogress = True
            elif gametype == game.GT_AI:
                # Watch AI.
                games.extend(createGame(stdscr, game.GT_AI))
                gameinprogress = True
            elif gametype == game.GT_AIVSAI:
                # AI vs AI.
                # Here we create both with game.GT_AI
                pass
            elif gametype == game.GT_HVSAI:
                # Human vs AI.
                # Here we create the games with GT_SINGLE and GT_AI
                pass
            else:
                # Fifth option. Clear the screen and quit by exiting the loop.
                stdscr.clear()
                break
        else:
            # There is a game (or games) in progress.
            for gameObj in games:
                if gameObj.gamerunning:
                    gameObj.run()
                else:
                    finishedGame = gameObj
            if finishedGame:
                games.remove(finishedGame)
                finishedGame = None
            if not games:
                # All games are done. Display the menu again.
                stdscr.clear()
                gameinprogress = False

if __name__ == "__main__":
    main()
    debug.end()
    curses.endwin()
