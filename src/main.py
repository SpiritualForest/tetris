# System-wide imports
import curses
import select
import time
import random
import sys
# Local (personal) imports
import block
import window
import debug


# TODO: implement AI

# Movement origins - we need this to determine whether the player caused the move,
# or the game moved the blocks downwards automatically.
O_PLAYER = "player" # can also be AI
O_GAME = "game"

blocks = (block.I, block.O, block.J, block.L, block.S, block.T, block.Z)
def getBlock():
    b = blocks[random.randint(0, 6)]
    return b

class Game:
    # Basically a wrapper class for everything else
    def __init__(self, windowObject):
        self.windowObject = windowObject
        self.gamerunning = False
        self.pause = False
        self.blockObj = None
        self.lines = 0
        self.movementOrigin = O_GAME
    
    def setBlock(self, blockObject):
        self.blockObj = blockObject

    def handleInput(self, r):
        #r, o, e = select.select([sys.stdin], [], [])
        if not r:
            debug.debug("Not R")
            return
        else:
            key = self.windowObject.window.getch()
            if key in (curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_DOWN):
                # Movement
                self.movementOrigin = O_PLAYER
                return (self.move, key)
            elif key == curses.KEY_UP:
                # Rotation
                return (self.rotate,)
            elif key in (ord("p"), ord("P")):
                # Pause or unpause the game
                if not self.pause:
                    self.pause = True
                else:
                    self.pause = False
            elif key in (ord("q"), ord("Q")):
                # Quit the game
                self.gamerunning = False
            else:
                # Do nothing
                pass

    def move(self, direction):
        # direction is actually a keystroke (curses.KEY_LEFT/RIGHT/DOWN)
        if not self.blockObj:
            # Tried to perform move() on a non existing object
            return
        if direction == curses.KEY_LEFT:
            # Left
            collision = self.isxCollision(block.D_LEFT)
            if collision:
                return
            else:
                self.blockObj.move(block.D_LEFT)
        elif direction == curses.KEY_RIGHT:
            # Right
            collision = self.isxCollision(block.D_RIGHT)
            if collision:
                return
            else:
                self.blockObj.move(block.D_RIGHT)
        else:
            # Down
            collision = self.isyCollision()
            if not collision:
                self.blockObj.move(block.D_DOWN)
            else:
                # Collision. What is the movement's origin?
                if self.movementOrigin == O_PLAYER:
                    # This is from the player. We don't need to do anything.
                    pass
                else:
                    self.dropblock()
                    return
        self.windowObject.clearCoordinates(self.blockObj.oldcoordinates)

    def dropblock(self):
        # This is from the game's automatic drop.
        # This means that the "movement interval" elapsed
        # and we need to check for line completion, and spawn a new block.
        coordinates = self.blockObj.coordinates
        for y in coordinates:
            # First we have to add all the block's coordinates to the grid.
            # Then we check for line completion
            xes = coordinates[y]
            newxes = []
            # generate the x: c for the grid. View window.py for more info.
            for x in xes:
                positions = (x, self.blockObj.colour)
                newxes.append(positions)
                try:
                    # Try to extend the y position on the grid
                    self.windowObject.grid[y].extend(newxes)
                except KeyError:
                    # y position doesn't exist. We must create it.
                    self.windowObject.grid[y] = newxes
                newxes = []
            # Check for line completion
            self.isCompleted(y)
        self.setBlock(None)
    
    def isCompleted(self, y):
        # Checks if all the values between startx and endx are present on grid line y.
        # If present, the line has been completed.
        gridline = self.windowObject.grid[y]
        linerange = range(self.windowObject.startx + 1, self.windowObject.endx)
        # Fuck you. Now I gotta form the gridline manually.
        gridpositions = []
        for xpos in gridline:
            gridpositions.append(xpos[0])
        for x in linerange:
            if x not in gridpositions:
                # Incomplete line. Abandon loop.
                return
        # If we reached here, the line is completed.
        self.lines += 1
        self.removeline(y)

    def removeline(self, y):
        # Clean out the line from the screen, remove it entirely from the grid,
        # and push all lines on the grid that are above it, one y position down.
        firstline = min(self.windowObject.grid)
        del self.windowObject.grid[y]
        for line in range(y, firstline, -1):
            # Push all these lines down
            self.windowObject.grid[line] = self.windowObject.grid[line - 1]
        # Redraw the entire screen
        del self.windowObject.grid[firstline]
        self.windowObject.redraw()

    def rotate(self):
        # Here we perform a collision check first,
        # and only then allow the block to rotate.
        # This is gonna work by examining the grid which surrounds the diameter of the block's rotation
        collision = False
        if collision:
            # Cannot rotate
            return
        else:
            self.blockObj.rotate()
            self.windowObject.clearCoordinates(self.blockObj.oldcoordinates)

    def isxCollision(self, direction):
        # only checks x values
        coordinates = self.blockObj.coordinates
        grid = self.windowObject.grid
        gridxes = []
        for y in coordinates:
            #debug.debug("isxCollision() - y value is: %s" % str(y))
            try:
                for xpos in grid[y]:
                    gridxes.append(xpos[0])
            except KeyError:
                # This y position doesn't exist.
                pass
            #debug.debug("Gridxes from isxCollision(): %s" % str(gridxes))
            for x in coordinates[y]:
                if direction == block.D_LEFT:
                    if x - 2 in gridxes or x - 2 == self.windowObject.startx:
                        # Collision
                        return True
                elif direction == block.D_RIGHT:
                    if x + 2 in gridxes or x + 2 == self.windowObject.endx:
                        # Collision
                        return True
        # If execution reached here, there were no collisions
        return False

    def isyCollision(self):
        # only checks y+1 values
        # origin tells us if it's from the player, or the automatic drop of the game.
        # if it's the game, and we have a collision, we trigger the end-of-block code
        # and check for line completion.
        coordinates = self.blockObj.coordinates
        grid = self.windowObject.grid
        for y in coordinates:
            ypo = y + 1 # "y plus one"
            if ypo in grid:
                # Check all x positions to make sure we aren't on descending onto them
                for xtuple in grid[ypo]:
                    xpos = xtuple[0]
                    if xpos in coordinates[y]:
                        # Collision detected.
                        return True
            else:
                # y isn't in the grid. Check wall collision.
                if y + 1 == self.windowObject.endy:
                    # Collision
                    return True
        # No collisions detected
        return False
        
def main():
    stdscr = curses.initscr()
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    windowObject = window.Window(stdscr)
    try:
        # Make the cursor invisible. Continue anyway if impossible
        curses.curs_set(0)
    except curses.error:
        pass
    # Start colour and initialize pairs
    curses.start_color()
    block.initpairs()
    # Create a game object and start the game
    game = Game(windowObject)
    game.gamerunning = 1
    interval = int(time.time()) + 1
    debug.debug("The interval: %s" % interval)
    while game.gamerunning:
        if not game.blockObj:
            if windowObject.starty + 1 in windowObject.grid:
                # Top line reached. Cannot spawn object. Game must end.
                game.gamerunning = 0
                return
            windowrangey = (windowObject.starty, windowObject.endy)
            windowrangex = (windowObject.startx, windowObject.endx)
            b = getBlock()
            blockObj = b(windowrangey, windowrangex)
            game.setBlock(blockObj)
        else:
            windowObject.draw(game.blockObj.coordinates, game.blockObj.colour)
            currenttime = int(time.time())
            if currenttime == interval:
                game.movementOrigin = O_GAME
                game.move(curses.KEY_DOWN)
                interval = currenttime + 1
            r, o, e = select.select([sys.stdin], [], [], 0.01)
            mwp = game.handleInput(r) # method with params
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
