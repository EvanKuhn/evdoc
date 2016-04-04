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

        self.frame_rows       = rows - Layout.TITLE_ROWS - Layout.PROMPT_ROWS
        self.frame_cols       = cols
        self.frame_start_row  = 1
        self.frame_start_col  = 0

        self.editor_rows      = self.frame_rows - 2
        self.editor_cols      = self.frame_cols - 2
        self.editor_start_row = self.frame_start_row + 1
        self.editor_start_col = self.frame_start_col + 1

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
    def __init__(self, layout, text):
        self.window = curses.newwin(layout.title_rows, layout.title_cols,
            layout.title_start_row, layout.title_start_col)
        start_col = (layout.title_cols - len(text)) / 2
        self.window.addstr(0, start_col, text, curses.A_BOLD)

    def redraw(self):
        self.window.refresh()

#==============================================================================
# The Frame simply draws a frame (around the editor)
#==============================================================================

class Frame:
    def __init__(self, layout):
        self.window = curses.newwin(layout.frame_rows, layout.frame_cols,
            layout.frame_start_row, layout.frame_start_col)

    def redraw(self):
        self.window.border()
        self.window.refresh()

#==============================================================================
# The Editor class displays the document
#==============================================================================

class Editor:
    def __init__(self, layout):
        self.document = evdoc.core.Document()
        # UI objects
        self.layout = layout
        self.window = curses.newwin(
            layout.editor_rows, layout.editor_cols,
            layout.editor_start_row, layout.editor_start_col)
        self.window.keypad(1)
        self._update_cursor()

    def getch(self):
        "Get a single character from the user"
        return self.window.getch()

    def addch(self, c):
        "Append a character to the editor. Does not redraw."
        self.document.addch(c)
        self._update_cursor()

    def backspace(self):
        "Delete the character to the left of the cursor. Does not redraw."
        self.document.backspace()

    def delete(self):
        "Delete the character at the cursor. Does not redraw."
        self.document.delete()

    def redraw(self):
        self.window.clear()

        # Draw the last N messages, where N is the number of visible rows
        row = 0
        for line in self.document.lines[0:self.layout.editor_rows]:
            self.window.addstr(row, 0, line)
            row += 1

        # Update the cursor and refresh
        self._update_cursor()
        self.window.refresh()

    def redraw_current_line(self):
        y, x = self.window.getyx()
        line = self.document.lines[y]
        self.window.addstr(y, 0, line)
        self.window.redrawln(y, 0)
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
        self.window.move(y, x)

#==============================================================================
# The Prompt class allows the user to enter commands
#==============================================================================

class Prompt:
    def __init__(self, layout):
        self.layout = layout
        self.window = curses.newwin(layout.prompt_rows, layout.prompt_cols,
            layout.prompt_start_row, layout.prompt_start_col)
        self.window.keypad(1)
        self.window.addstr('> ')

    def move(self, y, x):
        self.window.move(y, x)

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
