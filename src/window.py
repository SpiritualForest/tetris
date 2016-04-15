# -*- coding: utf-8 -*-
import debug
import curses
# Window class

# Window border characters - found these at https://en.wikipedia.org/wiki/Box-drawing_character
WB_UL = "┌" # Upper left
WB_BL = "└" # Bottom left
WB_UR = "┐" # Upper right
WB_BR = "┘" # Bottom right
WB_WALL_V = "│" # "Window Border Wall Vertical" - y
WB_WALL_H = "─" # "Window Border Wall Horizontal" - x

class Window:
    def __init__(self, stdscr):
        self.window = stdscr # this is stdscr
        self.maxy, self.maxx = self.window.getmaxyx()
        # Configurable size?
        self.sizey = 25
        self.sizex = 27
        self.drawWinBorder()
        # The grid will be a dictionary of "y: [(x, c), (x, c), (x, c), (x, c), (x, c), ...]" positions. c stands for colour.
        self.grid = {}

    def drawWinBorder(self):
        # Draw the window's border
        self.starty = y = int((self.maxy / 2) - self.sizey / 2)
        self.startx = x = int((self.maxx / 2) - (self.sizex / 2) - 6)
        self.endy = endy = y + self.sizey
        self.endx = endx = x + self.sizex
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

