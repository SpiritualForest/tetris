import curses
import debug

# I J L O S T Z

# init colour pairs

def initpairs():
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_GREEN) # 1 is green
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLUE) # 2 is blue
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_RED) # 3 is red
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA) # 4 is magenta
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_YELLOW) # 5 is yellow
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_CYAN) # 6 is cyan
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_WHITE) # 7 is white

C_GREEN = 1
C_BLUE = 2
C_RED = 3
C_MAGENTA = 4
C_YELLOW = 5
C_CYAN = 6
C_WHITE = 7

# Directional constants
D_LEFT = "left"
D_RIGHT = "right"
D_DOWN = "down"
D_UP = "up"

class Block:
    def __init__(self, rangey, rangex):
        self.oldcoordinates = {} # Used for updating the screen
        self.rotationcoordinates = []
        self.starty, self.endy = rangey
        self.startx, self.endx = rangex
        self.currentrotation = 0 # first rotation
        # Generate the coordinates. The values are from the child blocks.
        self.coordinates = self.map(self.width, self.cmap)
        for rmap in self.rotations:
            # rmap is a hash table
            rcmap = self.map(self.width, rmap)
            self.rotationcoordinates.append(rcmap)

        del self.rotations
        del self.cmap

    def rotate(self):
        self.oldcoordinates = self.coordinates
        rotation = self.rotationcoordinates[self.currentrotation]
        self.coordinates = rotation
        self.currentrotation += 1
        if self.currentrotation > len(self.rotationcoordinates) - 1:
            self.currentrotation = 0

    def map(self, width, cmap):
        # maps the coordinates of the block to (y, x) positions
        # according to width and height
        xes = []
        coordinates = {}
        for y in cmap.keys():
            # y values are numbered according to the height of the block
            # if a block's cmap has 2 keys in it, that means its height is 2.
            # on each y iteration we reset the x position to the center position
            pos = getCenter(width, self.startx, self.endx)
            mappers = cmap[y]
            for x in mappers:
                if not x:
                    # Don't draw in this position
                    # Increase pos by 2 because each position consists of two (y, x) elements
                    pos = pos + 2
                    continue
                else:
                    # Draw here.
                    xes.extend([pos, pos + 1])
                    pos = pos + 2
            coordinates[y + self.starty] = xes
            xes = []
        # return the resulting dictionary
        return coordinates
    
    def shiftCoordinates(self, cmap, direction):
        # Shifts the coordinates of cmap according to direction
        # right == x+2, left == x-2, down == y+1
        newmap = {}
        xes = []
        push = False
        newx = 0
        for y in cmap:
            # down
            if direction == D_DOWN:
                newmap[y + 1] = cmap[y]
                if y + 1 == self.endy:
                    # hit bottom border, push coordinates up
                    push = D_UP
            elif direction == D_UP:
                newmap[y - 1] = cmap[y]
            else:
                for x in cmap[y]:
                    # left
                    if direction == D_LEFT:
                        newx = x - 2
                        xes.append(newx)
                        if newx == self.startx:
                            # we've hit the window border, push the coordinates to the right
                            push = D_RIGHT
                    # right
                    elif direction == D_RIGHT:
                        newx = x + 2
                        xes.append(newx)
                        if newx == self.endx:
                            # hit the border, push coordinates to the left
                            push = D_LEFT
                newmap[y] = xes
                xes = []
        if push:
            newmap = self.shiftCoordinates(newmap, push)
        return newmap

    def move(self, direction):
        # Handles movement
        self.oldcoordinates = self.coordinates        
        self.coordinates = self.shiftCoordinates(self.oldcoordinates, direction)
        # Now the rotation coordinates
        newrotations = {}
        nrc = [] # new rotation coordinates
        for rotations in self.rotationcoordinates:
            # rotations is a dictionary
            newrotations = self.shiftCoordinates(rotations, direction)
            nrc.append(newrotations)
        self.rotationcoordinates = nrc

def getCenter(width, start, end):
    # Gets the middle "x" between start and end according to width
    drawrange = end - start
    result = int((drawrange / 2) - (width / 2) + start)
    return result

class I(Block):
    def __init__(self, rangey, rangex):
        self.colour = C_MAGENTA
        self.cmap = { 1: (1, 1, 1, 1) }
        self.rotations = (
                {
                    1: (0, 1, 0, 0),
                    2: (0, 1, 0, 0),
                    3: (0, 1, 0, 0),
                    4: (0, 1, 0, 0)
                },
                self.cmap
            )
        self.width = 8
        super().__init__(rangey, rangex)


class O(Block):
    def __init__(self, rangey, rangex):
        self.colour = C_BLUE
        self.cmap = {
                1: (1, 1),
                2: (1, 1)
                }
        self.rotations = (self.cmap, self.cmap)
        self.width = 4
        super().__init__(rangey, rangex)

class J(Block):
    def __init__(self, rangey, rangex):
        self.colour = C_YELLOW
        self.cmap = {
                1: (1, 0, 0, 0),
                2: (1, 1, 1, 0)
                }
        self.rotations = (
                {
                    1: (0, 1, 0, 0),
                    2: (0, 1, 0, 0),
                    3: (1, 1, 0, 0)
                },
                {
                    1: (1, 1, 1, 0),
                    2: (0, 0, 1, 0),
                },
                {
                    1: (1, 1, 0, 0),
                    2: (1, 0, 0, 0),
                    3: (1, 0, 0, 0)
                },
                self.cmap
            )
        self.width = 4
        super().__init__(rangey, rangex)

class L(Block):
    def __init__(self, rangey, rangex):
        self.colour = C_WHITE
        self.cmap = {
                1: (0, 0, 0, 1),
                2: (0, 1, 1, 1)
                }
        self.rotations = (
                {
                    1: (0, 0, 1, 1),
                    2: (0, 0, 0, 1),
                    3: (0, 0, 0, 1)
                },
                {
                    1: (0, 1, 1, 1),
                    2: (0, 1, 0, 0),
                },
                {
                    1: (0, 1, 0, 0),
                    2: (0, 1, 0, 0),
                    3: (0, 1, 1, 0)
                },
                self.cmap
            )
        self.width = 8
        super().__init__(rangey, rangex)

class S(Block):
    def __init__(self, rangey, rangex):
        self.colour = C_GREEN
        self.cmap = {
                1: (0, 0, 1, 1),
                2: (0, 1, 1, 0)
                }
        self.rotations = (
                {
                    1: (0, 1, 0, 0),
                    2: (0, 1, 1, 0),
                    3: (0, 0, 1, 0)
                },
                self.cmap
            )
        self.width = 8
        super().__init__(rangey, rangex)

class T(Block):
    def __init__(self, rangey, rangex):
        # Although this block's original width should have been 6,
        # this causes a bug, which is fixed by increasing its width to 8,
        # so that the map() method will position it further to the right.
        self.colour = C_CYAN
        self.cmap = {
                1: (1, 1, 1, 0),
                2: (0, 1, 0, 0)
                }
        self.rotations = (
                {
                    1: (1, 0, 0, 0),
                    2: (1, 1, 0, 0),
                    3: (1, 0, 0, 0)
                },
                {
                    1: (0, 1, 0, 0),
                    2: (1, 1, 1, 0)
                },
                {
                    1: (0, 0, 1, 0),
                    2: (0, 1, 1, 0),
                    3: (0, 0, 1, 0)
                },
                self.cmap
            )
        self.width = 8
        super().__init__(rangey, rangex)

class Z(Block):
    def __init__(self, rangey, rangex):
        self.colour = C_RED
        self.cmap = {
                1: (0, 1, 1, 0),
                2: (0, 0, 1, 1)
                }
        self.rotations = (
                {
                    1: (0, 0, 1, 0),
                    2: (0, 1, 1, 0),
                    3: (0, 1, 0, 0)
                },
                self.cmap
            )
        self.width = 8
        super().__init__(rangey, rangex)
