# -*- coding: utf-8 -*-
import debug
import curses

# Window border characters - found these at https://en.wikipedia.org/wiki/Box-drawing_character
WB_UL = "┌" # Upper left
WB_BL = "└" # Bottom left
WB_UR = "┐" # Upper right
WB_BR = "┘" # Bottom right
WB_WALL_V = "│" # "Window Border Wall Vertical" - y
WB_WALL_H = "─" # "Window Border Wall Horizontal" - x

class Window:
    def __init__(self, stdscr, yposition=0, xposition=6, sizey=25, sizex=27):
        # By default we create a game window. However, there could be other types of windows as well.
        self.window = stdscr # this is stdscr
        self.stdscrmaxy, self.stdscrmaxx = self.window.getmaxyx()
        # Configurable size?
        self.sizey = sizey
        self.sizex = sizex
        self.initWindow(yposition, xposition)
        # The grid will be a dictionary of "y: [(x, c), (x, c), (x, c), (x, c), (x, c), ...]" positions. c stands for colour.
        self.grid = {}

    def initWindow(self, yposition, xposition):
        # Initializes the window
        self.starty = int((self.stdscrmaxy / 2) - (self.sizey / 2) - yposition)
        self.startx = int((self.stdscrmaxx / 2) - (self.sizex / 2) - xposition)
        self.endy = self.starty + self.sizey
        self.endx = self.startx + self.sizex
        self.rangey = (self.starty, self.endy)
        self.rangex = (self.startx, self.endx)
        self.drawWinBorder()

    def reposition(self, y, x):
        # Resets the window's startx and starty,
        # and repositions the window according to the size.
        self.startx = x
        self.starty = y
        self.endx = x + self.sizex
        self.endy = y + self.sizey
        # TODO: rewrite grid coordinates here. Otherwise display gets fucked when this method is called.

    def drawWinBorder(self):
        # Draws the window's borders
        y = self.starty
        x = self.startx
        endy = self.endy
        endx = self.endx        
        # Draw the corners
        self.window.addstr(y, x, WB_UL)
        self.window.addstr(endy, x, WB_BL)
        self.window.addstr(y, endx, WB_UR)
        self.window.addstr(endy, endx, WB_BR)
        # Now the vertical walls
        for posy in range(y + 1, endy):
            self.window.addstr(posy, x, WB_WALL_V)
            self.window.addstr(posy, endx, WB_WALL_V)
        # Now draw the horizontal walls
        for posx in range(x + 1, endx):
            self.window.addstr(y, posx, WB_WALL_H)
            self.window.addstr(endy, posx, WB_WALL_H)

    def draw(self, coordinates, colour):
        # Draws at the coordinates with colour.
        for y in coordinates:
            for x in coordinates[y]:
                self.window.addstr(y, x, "#", curses.color_pair(colour))
        self.window.refresh()

    def clearPosition(self, position):
        y, x = position
        self.window.addstr(y, x, " ")

    def clearCoordinates(self, coordinates):
        # hash table
        for y in coordinates:
            for x in coordinates[y]:
                self.clearPosition((y, x))

    def redraw(self):
        # redraws the entire screen according to grid positions.
        self.window.clear()
        self.drawWinBorder()
        grid = self.grid
        for y in grid:
            for xpos in grid[y]:
                x, colour = xpos
                self.window.addstr(y, x, "#", curses.color_pair(colour))
