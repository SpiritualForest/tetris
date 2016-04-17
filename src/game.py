# System-wide imports
import random
import curses
import time
# Local (personal) imports
import block
import window
import debug

# TODO: implement levels and AI. Improve display. Add stats.
# TODO: allow game.dropblock() to be triggered when a user repeatedly presses down key on a collision.
# FIXME: IMPROVE READABILITIY!!!
# FIXME: implement collision check on rotations.
# FIXME: interval reduction on 10 lines causes the game to freeze

# Movement origins - we need this to determine whether the player caused the move,
# or the game moved the blocks downwards automatically.
O_PLAYER = "player" # can also be AI
O_GAME = "game"

class Game:
    # Basically a wrapper class for everything else
    def __init__(self, stdscr):
        self.windowObject = window.Window(stdscr)
        self.gamerunning = False
        self.pause = False
        self.blockObj = None
        self.nextblock = None # used for showing the player what the next block is
        self.lines = 0
        self.interval = 1 # time that has to pass between each automatic downwards movement of a block
        self.movementOrigin = O_GAME
        self.blocks = (block.I, block.O, block.J, block.L, block.S, block.T, block.Z)
    
    def setBlock(self, blockObject):
        self.blockObj = blockObject
    
    def hasblock(self):
        if not self.blockObj:
            return False
        else:
            return True

    def spawnBlock(self):
        b = self.blocks[random.randint(4, 5)]
        return b

    def handleInput(self, r):
        # FIXME: Totally reimplement this method
        if r:
            key = self.windowObject.window.getch()
            if key in (curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_DOWN):
                # Movement
                self.movementOrigin = O_GAME # For testing.
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
                    # Interval passed. Block can no longer be moved. Drop it.
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
            if self.isCompleted(y):
                self.removeline(y)
        # "Unscope" the block object
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
        collision = False
        # FIXME: Actually implement the collision detection
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
