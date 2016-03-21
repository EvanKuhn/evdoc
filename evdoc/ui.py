import curses
import os
import evdoc

#==============================================================================
# Simple class to calculate the layout of our UI and windows.
#==============================================================================

class Layout:
    TITLE_ROWS = 1
    PROMPT_ROWS = 1

    def __init__(self):
        "Determine the terminal size, and size of each window"
        rows, cols = Layout.terminal_size()

        # Save terminal size
        self.terminal_rows = rows
        self.terminal_cols = cols

        # Calculate dimensions of each window
        self.title_rows       = Layout.TITLE_ROWS
        self.title_cols       = cols
        self.title_start_row  = 0
        self.title_start_col  = 0

        self.editor_rows      = rows - Layout.TITLE_ROWS - Layout.PROMPT_ROWS
        self.editor_cols      = cols
        self.editor_start_row = 1
        self.editor_start_col = 0

        self.prompt_rows      = Layout.PROMPT_ROWS
        self.prompt_cols      = cols
        self.prompt_start_row = rows - 1
        self.prompt_start_col = 0

    @staticmethod
    def terminal_size():
        "Return the current terminal size, as a tuple of (rows, cols)"
        rows, cols = os.popen('stty size', 'r').read().split()
        return (int(rows), int(cols))

#==============================================================================
# This just displays the title
#==============================================================================

class Title:
    def __init__(self, layout, screen, text):
        self.window = curses.newwin(layout.title_rows, layout.title_cols,
            layout.title_start_row, layout.title_start_col)
        start_col = (layout.title_cols - len(text)) / 2
        self.window.addstr(0, start_col, text, curses.A_BOLD)

    def redraw(self):
        self.window.refresh()

#==============================================================================
# The Editor class displays the document
#==============================================================================

class Editor:
    def __init__(self, layout, screen):
        self.document = evdoc.core.Document()
        # UI objects
        self.layout = layout
        self.screen = screen
        self.window = curses.newwin(layout.editor_rows, layout.editor_cols,
            layout.editor_start_row, layout.editor_start_col)
        self.window.keypad(1)
        # Because we have a border, the number of visible rows/cols is fewer
        self.visible_rows = self.layout.editor_rows - 2
        self.visible_cols = self.layout.editor_cols - 2
        self.min_row = 1
        self.max_row = self.visible_rows
        self.min_col = 1
        self.max_col = self.visible_cols
        self.row_offset = 0
        self.col_offset = 0
        self._update_cursor()

    def getch(self):
        "Get a single character from the user"
        return self.window.getch()

    def addch(self, c):
        "Append a character to the editor. Does not redraw."
        self.document.addch(c)

    def redraw(self):
        self.window.clear()
        self.window.border(0)

        # Draw the last N messages, where N is the number of visible rows
        row = 1
        for line in self.document.lines[0:self.visible_rows]:
            self.window.addstr(row, 1, line)
            row += 1

        # Update the cursor and refresh
        self._update_cursor()
        self.window.refresh()

    def redraw_current_line(self):
        y, x = self.window.getyx()
        line = self.document.lines[y-1]
        self.window.addstr(y, 1, line)
        self.window.redrawln(y, 1)
        self.window.move(y, x)
        self.window.refresh()

    def move_up(self):
        self.document.move_up()
        self._update_cursor()

    def move_down(self):
        self.document.move_down()
        self._update_cursor()

    def move_left(self):
        self.document.move_left()
        self._update_cursor()

    def move_right(self):
        self.document.move_right()
        self._update_cursor()

    def _update_cursor(self):
        "Update the window cursor based on the document cursor"
        y, x = self.document.getyx()
        self.window.move(y+1, x+1)

#==============================================================================
# The Prompt class allows the user to enter commands
#==============================================================================

class Prompt:
    def __init__(self, layout, screen):
        self.layout = layout
        self.screen = screen
        self.window = curses.newwin(layout.prompt_rows, layout.prompt_cols,
            layout.prompt_start_row, layout.prompt_start_col)
        self.window.keypad(1)
        self.window.addstr('> ')

    def getch(self):
        "Get a single character from the user"
        return self.window.getch()

    def getstr(self):
        "Get an input string from the user"
        return self.window.getstr()

    def redraw(self):
        "Redraw the prompt window"
        self.window.refresh()

    def reset(self):
        "Reset the prompt to '> ' and redraw"
        self.window.clear()
        self.window.addstr('> ')
        self.redraw()
