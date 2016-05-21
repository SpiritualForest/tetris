# -*- coding: utf-8 -*-
import debug
import curses
import sys
import select

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

    def extractxes(self, grid, y):
        # Generates a list of all the x positions in a grid[y] position
        if y not in grid:
            return
        xes = []
        for xtuple in grid[y]:
            x = xtuple[0]
            xes.append(x)
        return xes

class NBWindow(Window):
    def __init__(self, gamewindow):
        # Next Block Window (displays the next block)
        # We position it according to the position of the main game window
        self.width = 14
        self.height = 4
        self.beginx = gamewindow.beginx - self.width
        self.beginy = gamewindow.beginy + self.height
        self.window = Window(self.height, self.width, self.beginy, self.beginx)

class MenuWindow(Window):
    # TODO: Make this more modular. Allow for dynamic specification of options.
    def __init__(self, maxyx):
        maxy, maxx = maxyx
        self.width = 15
        self.height = 7 # We have four options
        self.beginy = int((maxy / 2) - (self.height / 2))
        self.beginx = int((maxx / 2) - (self.width / 2))
        self.window = Window(self.height, self.width, self.beginy, self.beginx)
        self.window.keypad(True)
        self.choices = {
                1: "Single player",
                2: "Watch AI",
                3: "AI vs AI",
                4: "Human vs AI",
                5: "Quit"
                }
        self.choice = 1
        # Display the options
        self.displaymenu()

    def displaymenu(self):
        self.window.clear()
        self.window.border()
        for choice in self.choices:
            self.window.addstr(choice, 1, self.choices[choice])
        self.showchoice()
        self.window.refresh()

    def showchoice(self):
        # Highlights the current choice
        self.window.addstr(self.choice, 1, self.choices[self.choice], curses.A_BOLD | curses.color_pair(9))

    def handleInput(self):
        r, w, e = select.select([sys.stdin], [], [], 0.1)
        if r:
            key = self.window.getch()
            if key == curses.KEY_DOWN:
                if self.choice < max(self.choices):
                    self.choice += 1
                else:
                    self.choice = min(self.choices)
                self.displaymenu()
            elif key == curses.KEY_UP:
                if self.choice > 1:
                    self.choice -= 1
                else:
                    self.choice = max(self.choices)
                self.displaymenu()
            elif key == 13:
                # Enter key, select choice.
                return True

