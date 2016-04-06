import curses
import curses.ascii
import os
import evdoc

#==============================================================================
# Simple class to calculate the layout of our UI and windows.
#==============================================================================

class Layout(object):
    TITLE_ROWS = 1
    PROMPT_ROWS = 1

    def __init__(self):
        "Determine the terminal size, and size of each window"
        self.update()

    def update(self):
        "Update the terminal size, and size of each window"
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
# Base window object for the app
#==============================================================================

class AppWindow(object):
    def __init__(self):
        self.dirty = False

    def set_dirty(self):
        "Set the window as dirty"
        self.dirty = True

    def is_dirty(self):
        "Get the dirty flag, indicating whether the window should be redrawn"
        return self.dirty

    def redraw(self):
        "Redraw the window and set the dirty flag to false"
        self.window.refresh()
        self.dirty = False

#==============================================================================
# This just displays the title
#==============================================================================

class Title(AppWindow):
    def __init__(self, layout, text):
        self.layout = layout
        self.text = text
        self.window = curses.newwin(layout.title_rows, layout.title_cols,
            layout.title_start_row, layout.title_start_col)
        self.update()

    def update(self):
        '''
        Update the window's contents. The window will not be redrawn until
        curses.doupdate() is called.
        '''
        self.window.resize(self.layout.title_rows, self.layout.title_cols)
        start_col = (self.layout.title_cols - len(self.text)) / 2
        self.window.clear()
        self.window.addstr(0, start_col, self.text, curses.A_BOLD)
        self.window.noutrefresh()
        self.set_dirty()

    def resize(self, layout):
        "Update the window size"
        self.layout = layout
        self.update()

#==============================================================================
# The Frame simply draws a frame (around the editor)
#==============================================================================

class Frame(AppWindow):
    def __init__(self, layout):
        self.layout = layout
        self.window = curses.newwin(layout.frame_rows, layout.frame_cols,
            layout.frame_start_row, layout.frame_start_col)

    def update(self):
        '''
        Update the window's contents. The window will not be redrawn until
        curses.doupdate() is called.
        '''
        self.window.resize(self.layout.frame_rows, self.layout.frame_cols)
        self.window.border()
        self.window.noutrefresh()
        self.set_dirty()

    def resize(self, layout):
        "Update the window size"
        self.layout = layout
        self.update()

#==============================================================================
# The EditBox class is basically a fancy window that supports a wider variety
# of keypresses. Text is stored internally in a Document object.
#==============================================================================

class EditBox(AppWindow):
    def __init__(self, rows, cols, start_row, start_col, logger=None):
        self.document  = evdoc.core.Document()
        self.logger    = logger
        self.rows      = rows
        self.cols      = cols
        self.start_row = start_row
        self.start_col = start_col
        self.scroll_x  = 0
        self.scroll_y  = 0
        self.window    = curses.newwin(rows, cols, start_row, start_col)
        self.window.keypad(1)
        self._resize(rows, cols, start_row, start_col)

    def update(self):
        '''
        Repopulate all contents of the window and move focus to it. The window
        will not be redrawn until curses.doupdate() is called.
        '''
        self._update_scroll()
        self._update_content()
        self._update_cursor()

    def _update_scroll(self):
        '''
        Update the X and Y scroll position of the window, if needed, to ensure
        that the location of the cursor in the document is in view. Returns
        true if updated, false if no changes made.
        '''
        changed = False
        y, x = self.document.getyx()

        # Update the horizontal scroll to make sure the cursor is visible
        if x < self.scroll_x or x >= self.scroll_x + self.cols:
            self.scroll_x = max(x - (self.cols / 2), 0)
            changed = True

        # Update the vertical scroll
        if y < self.scroll_y:
            self.scroll_y -= 1
            changed = True
        elif y >= self.scroll_y + self.rows:
            self.scroll_y += 1
            changed = True

        return changed

    def _update_content(self):
        self.window.clear()

        # Draw the last N messages, where N is the number of visible rows
        row = 0
        for line in self.document.lines[self.scroll_y : self.scroll_y + self.rows]:
            substr = line[self.scroll_x : self.scroll_x + self.cols]
            self.window.addstr(row, 0, substr)
            row += 1

        # Update the cursor and refresh
        self.window.noutrefresh()
        self.set_dirty()

    def _update_cursor(self):
        '''
        Update the cursor location to match the document. Assumes scrolling
        has been updated.
        '''
        y, x = self.document.getyx()
        self.window.move(y - self.scroll_y, x - self.scroll_x)

    def _resize(self, rows, cols, start_row, start_col):
        '''
        Update the window size. The window will not be redrawn until
        curses.doupdate() is called.
        '''
        changed = False

        if self.rows != rows or self.cols != cols:
            self.rows = rows
            self.cols = cols
            self.window.resize(rows, cols)
            changed = True

        if self.start_row != start_row or self.start_col != start_col:
            self.start_row = start_row
            self.start_col = start_col
            self.window.mvwin(start_row, start_col)
            changed = True

        if changed:
            self.update()

    def clear(self):
        "Clear the editbox of all contents and redraw it"
        self.document.clear()
        self.window.clear()
        self.redraw()   #TODO: do not redraw automatically (?)

    def contents(self):
        "Get the contents of the EditBox, as a string"
        return "\n".join(self.document.lines)

    def getch(self):
        "Get a single character from the user"
        return self.window.getch()

    def addch(self, c):
        "Append a character to the editor. Does not redraw."
        self.document.addch(c)

    def backspace(self):
        "Delete the character to the left of the cursor. Does not redraw."
        self.document.backspace()

    def delete(self):
        "Delete the character at the cursor. Does not redraw."
        self.document.delete()

    def focus(self):
        "Move focus to this window"
        self.redraw()

    def redraw_current_line(self):
        "Redraw the current line"
        y, x = self.window.getyx()
        line = self.document.lines[y]
        substr = line[self.scroll_x : self.scroll_x + self.cols]
        self.window.addstr(y, 0, substr)
        self.window.redrawln(y, 0)
        self.window.move(y, x)

    def move_up(self):
        self.document.move_up()
        self.update()

    def move_down(self):
        self.document.move_down()
        self.update()

    def move_left(self):
        self.document.move_left()
        self.update()

    def move_right(self):
        self.document.move_right()
        self.update()

    def edit(self, terminators=[curses.ascii.ESC]):
        '''
        Collect input keystrokes from the user. When a given terminator character
        is received, stop and return it.
        - Always ignores the Escape character.
        - Always returns a KEY_RESIZE character.
        '''
        while True:
            # Get input
            c = self.getch()

            if c in terminators:
                return c
            if c == curses.KEY_RESIZE:
                return c

            # Take action
            if c == curses.ascii.LF:
                self.scroll_x = 0
                self.addch(c)
                self.update()
            elif c == curses.ascii.TAB:
                pass
            elif curses.ascii.isprint(c):
                self.addch(c)
                self.update()
            elif c == curses.KEY_UP:
                self.move_up()
            elif c == curses.KEY_DOWN:
                self.move_down()
            elif c == curses.KEY_LEFT:
                self.move_left()
            elif c == curses.KEY_RIGHT:
                self.move_right()
            elif c == curses.ascii.DEL:
                self.backspace()
                self.update()
            elif c == curses.KEY_DC:
                self.delete()
                self.update()
            elif c == curses.KEY_MOUSE:
                id, x, y, z, bstate = curses.getmouse()
                self.logger.log("Mouse event: id=%d, x=%d, y=%d, z=%d, bstate=%d" %
                    (id, x, y, z, bstate))

            # Redraw the window if dirty
            if self.is_dirty():
                self.redraw()

            # Debug output
            win_y, win_x = self.window.getyx()
            doc_y, doc_x = self.document.getyx()
            self.logger.log("doc: (%d, %d)  win: (%d, %d) scroll: (%d, %d) dims: (%d, %d)" %
                (doc_y, doc_x, win_y, win_x, self.scroll_y, self.scroll_x, self.rows, self.cols))

#==============================================================================
# The Editor class displays the document
#==============================================================================

class Editor(EditBox):
    def __init__(self, layout, logger=None):
        self.layout = layout
        super(evdoc.ui.Editor, self).__init__(
            layout.editor_rows,
            layout.editor_cols,
            layout.editor_start_row,
            layout.editor_start_col,
            logger)

    def resize(self, layout):
        "Update the window size"
        self.layout = layout
        super(evdoc.ui.Editor, self)._resize(
            layout.editor_rows,
            layout.editor_cols,
            layout.editor_start_row,
            layout.editor_start_col)

#==============================================================================
# The Prompt class allows the user to enter commands
#==============================================================================

class Prompt(EditBox):
    def __init__(self, layout, logger=None):
        self.layout = layout
        super(evdoc.ui.Prompt, self).__init__(
            layout.prompt_rows,
            layout.prompt_cols,
            layout.prompt_start_row,
            layout.prompt_start_col,
            logger)

    def resize(self, layout):
        "Update the window size"
        self.layout = layout
        super(evdoc.ui.Prompt, self)._resize(
            layout.prompt_rows,
            layout.prompt_cols,
            layout.prompt_start_row,
            layout.prompt_start_col)

    def edit(self):
        "Get user input from the prompt. Returns the terminator character typed."
        return super(Prompt, self).edit([curses.ascii.ESC, curses.ascii.LF])
