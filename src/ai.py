# AI Class. This is my first ever take on AI.
# It gives commands by setting an attribute, 
# which is then accesed by a .getch() method
# in the game instance's handleInput() method.

import curses

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

    def getCommand(self):
        # Returns the command that the AI wants to perform.
        # This is actually a curses.KEY_* value.
        return self.command
