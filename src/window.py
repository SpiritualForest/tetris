# -*- coding: utf-8 -*-
import debug
import curses

class Window:
    def __init__(self, height, width, beginy, beginx):
        self.height = height
        self.width = width
        self.beginy = beginy
        self.beginx = beginx
        self.initWindow()

    def initWindow(self):
        # Initializes the window
        self.window = curses.newwin(self.height, self.width, self.beginy, self.beginx)
        self.starty = self.startx = 0
        self.endy = self.height - 1
        self.endx = self.width - 1
        self.rangey = (self.starty, self.endy)
        self.rangex = (self.startx, self.endx)
        self.window.border()
        self.window.refresh()

    def draw(self, coordinates, colour):
        # Draws at the coordinates with colour.
        for y in coordinates:
            for x in coordinates[y]:
                self.window.addstr(y, x, "#", curses.color_pair(colour))
        self.window.refresh()

    def __getattr__(self, attr):
        return getattr(self.window, attr)

class GameWindow(Window):
    def __init__(self, height, width, maxy, maxx):
        self.beginy = int((maxy / 2) - (height / 2))
        self.beginx = int((maxx / 2) - (width / 2) - 6)
        # The grid will be a dictionary of "y: [(x, c), (x, c), (x, c), (x, c), (x, c), ...]" positions. c stands for colour.
        self.grid = {}
        self.window = Window(height, width, self.beginy, self.beginx)
        self.window.keypad(True)

    def clearPosition(self, position):
        y, x = position
        self.window.addstr(y, x, " ")

    def clearCoordinates(self, coordinates):
        # hash table
        for y in coordinates:
            for x in coordinates[y]:
                self.clearPosition((y, x))

    def redraw(self):
        # redraws the window according to grid positions.
        self.window.erase()
        self.window.border()
        grid = self.grid
        for y in grid:
            for xpos in grid[y]:
                x, colour = xpos
                self.window.addstr(y, x, "#", curses.color_pair(colour))

class StatsWindow(Window):
    def __init__(self, height, width, maxy, maxx):
        pass

