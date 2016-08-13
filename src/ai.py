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
import debug

class AI:
    def __init__(self, game):
        # The AI has access to its game object, allowing it to directly call methods in order to move and rotate the block, etc.
        self.game = game 
        self.window = game.windowObject
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
        # Encapsulation function for computing the various heuristics.
        grid = self.window.grid
        self.game.dropblock(False) # False indicates that the changes are temporary.
        # Actual checks
        lines = self.checklines(grid)
        holes = self.checkholes(grid)
        height = self.checkheight(grid)
        bumpiness = self.checkbumpiness(grid)
        # NOTE: Remember to undrop the block!
        self.game.undrop()
        if lines:
            debug.debug("AI detected completed lines: %s" % lines)
        if holes:
            debug.debug("AI detected new holes: %s" % holes)
        if bumpiness:
            debug.debug("AI detected bumpiness level: %s" % bumpiness)
        debug.debug("Height of grid: %s" % height)

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
        # We divide by two because each "x unit" of a block is actually made up of 2 x positions.
        # So the I block actually takes up 8 x spaces when it's vertical, not 4.
        return int(holes / 2)
    
    def formxlist(self, grid):
        # Forms the "x list" so we can calculate height and bumpiness
        xlist = []
        temp = []
        add = True
        for y in grid:
            if add:
                # Since each column is made up of two x positions and one y position, we don't need to add both.
                # We skip over one of them each time.
                xes = self.window.extractxes(grid, y)
                for x in xes:
                    temp.append(y)
                xlist.append(temp)
                temp = []
                add = False
            else:
                add = True
        return xlist

    def checkheight(self, grid):
        # We check the height of the grid.
        # In order to account for holes, we start the total sum with checkholes()
        total = self.checkholes(grid)
        xlist = self.formxlist(grid)
        # Now we have a list.
        return sum(len(x) for x in xlist)

    def checkbumpiness(self, grid):
        # Here we compute the absolute value of between all two adjacent columns.
        # We check holes as well in order to account for them.
        xlist = self.formxlist(grid)
        total = self.checkholes(grid)
        for i, x in enumerate(xlist[::2]):
            try:
                length = len(x) - len(xlist[i + 1])
                total += length
            except IndexError:
                total += len(xlist[i])
        return total
