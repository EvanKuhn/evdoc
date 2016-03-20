import curses.ascii

#==============================================================================
# Basic document object, with lines separated
#==============================================================================

class Document:
    def __init__(self):
        self.lines = ['']
        self.line = 0
        self.col = 0
        pass

    def set_cursor(self, line, col):
        "Set the cursor location. Will keep cursor within bounds of the document."
        max_line = len(self.lines) - 1
        self.line = max_line if line > max_line else line
        max_col = len(self.lines[self.line])
        self.col = max_col if col > max_col else col

    def get_cursor(self):
        "Return the cursor location as (line,col)"
        return (self.line, self.col)

    def addchar(self, c):
        '''
        Insert a character at the current cursor location. Ignores
        non-printable characters.
        '''
        if c == "\n":
            self._insert_new_line()
        elif curses.ascii.isprint(c):
            self._insert_string(c)

    def addstr(self, str):
        "Insert a string at the current cursor location. Handles newline chars."
        start = 0
        length = len(str)
        while start < length:
            # Look for the next newline, or end of string
            end = start
            while end < length and str[end] != "\n":
                end += 1
            # Insert the string, and optionally a newline
            self._insert_string(str[start:end])
            if end < length and str[end] == "\n":
                self._insert_new_line()
            start = end + 1

    def _insert_string(self, str):
        '''
        Insert a string at the current cursor location. Assumes the string
        does not contain a newline char.
        '''
        if len(str) > 0:
            # Split the current line into left and right sides
            line = self.lines[self.line]
            lhs = line[:self.col]
            rhs = line[self.col:]
            # Create the new line
            self.lines[self.line] = lhs + str + rhs
            # Move the cursor
            self.col += len(str)

    def _insert_new_line(self):
        "Insert a newline at the current cursor location"
        # Split the current line into left and right sides
        line = self.lines[self.line]
        lhs = line[:self.col]
        rhs = line[self.col:]
        # Insert a new line, which equals the right side). The existing line
        # becomes the left side.
        self.lines = self.lines[:self.line+1] + [rhs] + self.lines[self.line+1:]
        self.lines[self.line] = lhs
        # Move the cursor
        self.line += 1
        self.col = 0

#==============================================================================
# Word-wrapped document
#==============================================================================

class WordWrappedDocument:
    def __init__(self, doc):
        pass
