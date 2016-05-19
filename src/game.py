# System-wide imports
import random
import curses
import time
import select
import sys
# Local (personal) imports
import block
import window
import debug

# TODO: implement levels and AI. Improve display. Add stats.
# TODO: allow game.dropblock() to be triggered when a user repeatedly presses down key on a collision.

# Movement origins - we need this to determine whether the player caused the move,
# or the game moved the blocks downwards automatically.
O_PLAYER = "player" # can also be AI
O_GAME = "game"
# Game type constants
GT_SINGLE = 1
GT_AI = 2
GT_AIVSAI = 3
GT_HVSAI = 4

class Game:
    # Basically a wrapper class for everything else
    def __init__(self, stdscr, human=True):
        self.maxyx = stdscr.getmaxyx()
        self.createWindows(stdscr)
        self.gamerunning = False
        self.pause = False
        self.blockObj = None
        self.lines = 0
        self.interval = 1 # time that has to pass between each automatic downwards movement of a block
        self.nextautomove = time.time() + self.interval
        self.downpress = 0 # used to enable the player to force-drop a block.
        self.movementOrigin = O_GAME
        self.humanplayer = human  # True by default
        self.aiObject = None
        self.blocks = (block.I, block.O, block.J, block.L, block.S, block.T, block.Z)
        self.nextblock = self.spawnBlock()
    
    def createWindows(self, stdscr):
        # Creates the game and new block windows. This is ugly.
        # First the game window
        height = 25
        width = 28
        maxy, maxx = self.maxyx
        self.windowObject = window.GameWindow(height, width, maxy, maxx)
        # Now the new block window
        beginx = self.windowObject.beginx
        beginy = self.windowObject.beginy
        nbx = beginx + block.getCenter(10, 0, width)
        self.nbw = window.NBWindow(self.windowObject)
        self.nbw.window.clear()
        self.nbw.window.refresh()
    
    def run(self):
        # This method ties everything together.
        # It will enable us to have multiple game instances as well.
        if not self.hasblock():
            if 1 in self.windowObject.grid:
                # Top line reached. Game ends.
                self.gamerunning = False
                return
            b = self.nextblock
            # Next block formation and displaying
            self.nextblock = self.spawnBlock()
            self.nbw.window.clear()
            nbobj = self.nextblock(self.nbw.window.rangey, self.nbw.window.rangex)
            self.nbw.window.draw(nbobj.coordinates, nbobj.colour)
            # Current block handling
            blockObject = b(self.windowObject.window.rangey, self.windowObject.window.rangex)
            self.setBlock(blockObject)
        else:
            # Draw the block on the window, automatically move, take input
            self.windowObject.draw(self.blockObj.coordinates, self.blockObj.colour)
            self.automove()
            self.handleInput()


    def setBlock(self, blockObject):
        self.blockObj = blockObject
    
    def hasblock(self):
        if not self.blockObj:
            return False
        else:
            return True

    def spawnBlock(self):
        b = self.blocks[random.randint(0, 6)]
        return b

    def canmove(self):
        # If the block "can move now" because the next automatic movement time had elapsed, return True.
        # If it can't yet, return False.
        if time.time() >= self.nextautomove:
            return True
        else:
            return False

    def automove(self, forced=False):
        # Checks whether the block can move downwards now.
        # If it can, moves it down and resets the next automatic movement time.
        if self.hasblock():
            if forced or self.canmove():
                self.movementOrigin = O_GAME
                self.move(curses.KEY_DOWN)
                self.nextautomove = time.time() + self.interval

    def handleInput(self):
        # This method handles input.
        # It can take input either from a human player, or an AI.
        key = None
        if self.humanplayer:
            r, w, e = select.select([sys.stdin], [], [], 0.01)
            if not r:
                return
            key = self.windowObject.window.getch()
        else:
            # Grab input from AI
            key = self.aiObject.getCommand()            
        # Actual functionality begins here.
        if key in (curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_DOWN):
            # Movement
            self.movementOrigin = O_PLAYER
            self.move(key)
        elif key == curses.KEY_UP:
            # Rotation
            self.rotate()
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
            debug.debug("Tried to perform move() on a non existing object")
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
                    self.downpress += 1
                    if self.downpress == 2:
                        self.downpress = 0
                        self.automove(True)
                        # We return here because automove()
                        # might cause dropblock() to trigger,
                        # which would set the block object to None.
                        return
                else:
                    # Interval passed. Block can no longer be moved. Drop it.
                    self.dropblock()
                    return
        # Clear the object's previous coordinates from the screen.
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
            if self.isCompleted(y):
                self.removeline(y)
                if self.lines % 10 == 0:
                    # Another 10 lines. Decrease the interval by 100 milliseconds
                    self.interval = self.interval - 0.250
        self.setBlock(None)
    
    def isCompleted(self, y):
        # The grid is a dictionary of y: (x, c) tuples with "c" being a colour code.
        # This function checks if the amount of tuples in grid line "y" is equal to the width of the window.
        # If it is, that means it's a full line.
        gridline = self.windowObject.grid[y]
        linerange = self.windowObject.endx - (self.windowObject.startx + 1)
        if len(gridline) != linerange:
            return False
        else:
            self.lines += 1
            return True

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
        nextrotation = self.blockObj.currentrotation
        nrc = self.blockObj.rotationcoordinates[nextrotation] # next rotation coordinates
        for y in nrc:
            try:
                gridline = self.windowObject.grid[y]
            except KeyError:
                gridline = []
            for xtuple in gridline:
                if xtuple[0] in nrc[y]:
                    # This position exists on the grid. It's impossible to rotate into it.
                    debug.debug("Rotation collision detected: (%s, %s)" % (y, xtuple[0]))
                    return
        self.blockObj.rotate()
        self.windowObject.clearCoordinates(self.blockObj.oldcoordinates)

    def isxCollision(self, direction):
        # only checks x values
        coordinates = self.blockObj.coordinates
        grid = self.windowObject.grid
        gridxes = []
        for y in coordinates:
            try:
                for xpos in grid[y]:
                    gridxes.append(xpos[0])
            except KeyError:
                # This y position doesn't exist.
                pass
            for x in coordinates[y]:
                if direction == block.D_LEFT:
                    if x - 2 in gridxes or x - 2 == self.windowObject.startx:
                        # Collision
                        return True
                elif direction == block.D_RIGHT:
                    if x + 2 in gridxes or x + 2 == self.windowObject.endx:
                        # Collision
                        return True
            gridxes = []
        # If execution reached here, there were no collisions
        return False

    def isyCollision(self):
        # only checks y+1 values
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
                if ypo == self.windowObject.endy:
                    # Collision
                    return True
        # No collisions detected
        return False
