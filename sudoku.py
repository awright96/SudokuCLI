import sys,os
import curses
from itertools import product
from pulp import *

class Sudoku:
    x_size = 19
    y_size = 38
    x_offset = 0
    y_offset = 0
    subboards = {}
    x_sub_off = 12
    y_sub_off = 6
    x_sub_size = 11
    y_sub_size = 6
    map = {}
    state = {}
    solutions = []
    win = None
    n = 0


    def __init__(self, win, x_offset, y_offset):
        self.win = win
        self.x_offset = x_offset
        self.y_offset = y_offset
        for i in product(range(3), repeat=2):
            item = (self.x_offset + 1 + i[0] * self.x_sub_off,
                    self.y_offset + 1 + i[1] * self.y_sub_off)
            self.subboards[i] = item
        for x in self.subboards.keys():
            offset = self.subboards.get(x)
            for i in product(range(3), repeat=2):
                self.map[(x[0] * 3 + i[0], x[1] * 3 + i[1])] = (offset[0] + 1 + i[0] * 4, offset[1] + i[1] * 2)
        for x in product(range(9), repeat=2):
            self.state[(x[0], x[1])] = '0'

    def draw_board(self):
        self.win.addstr( 0 + self.y_offset, self.x_offset, "╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗")
        self.win.addstr( 1 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr( 2 + self.y_offset, self.x_offset, "╟           ╫           ╫           ╢")
        self.win.addstr( 3 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr( 4 + self.y_offset, self.x_offset, "╟           ╫           ╫           ╢")
        self.win.addstr( 5 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr( 6 + self.y_offset, self.x_offset, "╠═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╣")
        self.win.addstr( 7 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr( 8 + self.y_offset, self.x_offset, "╟           ╫           ╫           ╢")
        self.win.addstr( 9 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr(10 + self.y_offset, self.x_offset, "╟           ╫           ╫           ╢")
        self.win.addstr(11 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr(12 + self.y_offset, self.x_offset, "╠═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╣")
        self.win.addstr(13 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr(14 + self.y_offset, self.x_offset, "╟           ╫           ╫           ╢")
        self.win.addstr(15 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr(16 + self.y_offset, self.x_offset, "╟           ╫           ╫           ╢")
        self.win.addstr(17 + self.y_offset, self.x_offset, "║           ║           ║           ║")
        self.win.addstr(18 + self.y_offset, self.x_offset, "╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝")
        for x in self.subboards.keys():
            offset = self.subboards.get(x)
            self.draw_subboard(offset[0], offset[1])

        if len(self.solutions) != 0:
            self.draw_state(state=self.solutions[self.n - 1], color=curses.color_pair(2) | curses.A_REVERSE, refresh=False)
        self.draw_state(state=self.state, refresh=False)

        self.win.refresh()
        return

    def draw_subboard(self, j, i):
        self.win.addstr(i,     j, "   │   │   ")
        self.win.addstr(i + 1, j, "───┼───┼───")
        self.win.addstr(i + 2, j, "   │   │   ")
        self.win.addstr(i + 3, j, "───┼───┼───")
        self.win.addstr(i + 4, j, "   │   │   ")
        self.win.refresh()

    def get_raw_state(self):
        return self.state

    def put_raw_state(self, x, y, val):
        self.state[(x, y)] = val
        self.draw_board()

    def draw_state(self, state, refresh=True, color=0):
        for x in state.keys():
            offset = self.map.get((x[0], x[1]))
            ch = state.get(x)
            if ch == '0':
                continue
            self.win.addstr(offset[1], offset[0], ch, color)
        if refresh:
            self.win.refresh()

    def solve(self):
        Sequence = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

        Vals = Sequence
        Rows = Sequence
        Cols = Sequence

        Boxes = []
        for i in range(3):
            for j in range(3):
                Boxes += [[(Rows[3 * i + k], Cols[3 * j + l]) for k in range(3) for l in range(3)]]

        prob = LpProblem("Sudoku Problem", LpMinimize)
        choices = LpVariable.dicts("Choice", (Vals, Rows, Cols), 0, 1, LpInteger)

        prob += 0, "Arbitrary Objective Function"

        # A constraint ensuring that only one value can be in each square is created
        for r in Rows:
            for c in Cols:
                prob += lpSum([choices[v][r][c] for v in Vals]) == 1, ""

        # The row, column and box constraints are added for each value
        for v in Vals:
            for r in Rows:
                prob += lpSum([choices[v][r][c] for c in Cols]) == 1, ""

            for c in Cols:
                prob += lpSum([choices[v][r][c] for r in Rows]) == 1, ""

            for b in Boxes:
                prob += lpSum([choices[v][r][c] for (r, c) in b]) == 1, ""

        for x in self.state.keys():
            val = self.state.get(x)
            if val != '0':
                prob += choices[str(val)][str(x[1] + 1)][str(x[0] + 1)] == 1, ""

        # The problem data is written to an .lp file
        prob.writeLP("Sudoku.lp")

        # The problem is solved using PuLP's choice of Solver
        prob.solve(CPLEX(msg=0))
        sol = {}

        # The status of the solution is printed to the screen
        if LpStatus[prob.status] == "Optimal":
            self.n += 1
            for r in Rows:
                for c in Cols:
                    for v in Vals:
                        if value(choices[v][r][c]) == 1 and self.state.get((int(c) - 1, int(r) - 1)) == '0':
                            sol[(int(c) - 1, int(r) - 1)] = v

            self.solutions.append(sol)

            prob += lpSum([choices[v][r][c] for v in Vals
                       for r in Rows
                       for c in Cols
                       if value(choices[v][r][c]) == 1]) <= 80
            self.win.addstr(24, 0, ("Found %d solutions" % self.n))
            self.win.refresh()
            self.draw_board()






def draw_main(stdscr):
    k = ord(' ')
    cursor_x = 0
    cursor_y = 0

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    sudo = Sudoku(stdscr, 2, 2)
    stdscr.refresh()

    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN or k == ord('j'):
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP or k == ord('k'):
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT or k == ord('l'):
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT or k == ord('h'):
            cursor_x = cursor_x - 1
        elif k == ord('s'):
            sudo.solve()
        elif k >= ord('1') and k <= ord('9'):
            sudo.put_raw_state(cursor_x, cursor_y, chr(k))
        elif k == 127:
            sudo.put_raw_state(cursor_x, cursor_y, '0')

        cursor_x = max(0, cursor_x)
        cursor_x = min(8, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(8, cursor_y)

        # Declaration of strings
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Render board
        sudo.draw_board()

        # Refresh the screen
        stdscr.refresh()
        pos = sudo.map.get((cursor_x, cursor_y))
        stdscr.move(pos[1], pos[0])


        # Wait for next input
        k = stdscr.getch()

def main():
    curses.wrapper(draw_main)

if __name__ == "__main__":
    main()
