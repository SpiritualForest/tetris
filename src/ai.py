# AI Class. This is my first ever take on AI.
# It gives commands by setting an attribute, 
# which is then accesed by a getCommand() method
# in the game instance's handleInput() method.

# We'll work with heuristics:
# 1. Aggregate height (minimize)
# 2. Complete lines (maximize)
# 3. Holes (minimize)
# 4. Bumpiness (minimize)

import curses
import copy
import debug

class AI:
    def __init__(self, window):
        # Window is the game's window object
        self.window = window
        self.command = None

    def setBlock(self, block):
        # Set the block object.
        # We don't actually do anything with this, except get the coordinates of the block,
        # which are required for calculations.
        self.blockObj = block
   
    def setNextBlock(self, block):
        # Set the next block
        self.nextblock = block

    def getCommand(self):
        # Returns the command that the AI wants to perform.
        # This is actually a curses.KEY_* value.
        return self.command

    def computeHeuristics(self):
        # First we generate the new grid on the game's actual grid.
        # However, there is no permanent modification to the game's real grid.
        grid = copy.deepcopy(self.window.grid)
        self.addblock(grid)
        lines = self.checklines(grid)
        holes = self.checkholes(grid)
        if lines:
            debug.debug("AI detected completed lines: %s" % lines)
        if holes:
            debug.debug("AI detected new holes: %s" % holes)
    
    def checklines(self, grid):
        # Checks how many lines will be completed on the grid
        linerange = self.window.endx - (self.window.startx + 1)
        lines = 0
        for y in grid:
            if len(grid[y]) == linerange:
                lines += 1
        return lines

    def checkholes(self, grid):
        # We need to go through all the grid's positions.
        # If a given y,x position is occupied, we check whether (y+1, x) is also occupied.
        # If it is, that means we have a hole.
        holes = 0
        for y in grid:
            xes = grid[y]
            for xtuple in xes:
                # This HAS to be an occupied position, as our grid is composed of:
                # y: [(x, c), (x, c), (x, c), (x, c), ...] positions.
                # Therefore if we can loop on it, it exists in the grid, and this y,x position is taken.
                if y+1 in grid:
                    x = xtuple[0]
                    exes = self.window.extractxes(grid, y+1) # "Extracted xes"
                    if x not in exes:
                        # Hole detected.
                        holes += 1
        return holes

    def addblock(self, grid):
        # Adds the block to the given grid, returns the result
        coordinates = self.blockObj.coordinates
        for y in coordinates:
            # First we have to add all the block's coordinates to the grid.
            xes = coordinates[y]
            newxes = []
            # generate the x: c for the grid. View window.py for more info.
            for x in xes:
                positions = (x, self.blockObj.colour)
                newxes.append(positions)
                try:
                    # Try to extend the y position on the grid
                    grid[y].extend(newxes)
                except KeyError:
                    # y position doesn't exist. We must create it.
                    grid[y] = newxes
                newxes = []
        return grid
