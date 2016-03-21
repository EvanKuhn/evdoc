import curses.ascii

#==============================================================================
# Basic document object, with lines separated
#==============================================================================

class Document:
    def __init__(self):
        self.lines = ['']
        self.y = 0
        self.x = 0
        pass

    def move(self, y, x):
        "Set the cursor location. Will keep cursor within bounds of the document."
        self.y = max(y, len(self.lines) - 1)
        self.x = max(x, len(self.lines[self.y]))

    def getyx(self):
        "Return the cursor location as (y,x)"
        return (self.y, self.x)

    def addch(self, c):
        '''
        Insert a character at the current cursor location. Ignores
        non-printable characters.
        '''
        if type(c) == int:
            c = chr(c)
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
            line = self.lines[self.y]
            lhs = line[:self.x]
            rhs = line[self.x:]
            # Create the new line
            self.lines[self.y] = lhs + str + rhs
            # Move the cursor
            self.x += len(str)

    def _insert_new_line(self):
        "Insert a newline at the current cursor location"
        # Split the current line into left and right sides
        line = self.lines[self.y]
        lhs = line[:self.x]
        rhs = line[self.x:]
        # Insert a new line, which equals the right side). The existing line
        # becomes the left side.
        self.lines = self.lines[:self.y+1] + [rhs] + self.lines[self.y+1:]
        self.lines[self.y] = lhs
        # Move the cursor
        self.y += 1
        self.x = 0

#==============================================================================
# Word-wrapped document
#==============================================================================

class WordWrappedDocument:
    def __init__(self, doc, width):
        self.doc = doc
        self.width = width
        self.lines = []     # Holds document location as tuple: (y, x, length)
        self.y = 0
        self.x = 0

    def move(self, y, x):
        '''
        Set the cursor location. Will keep cursor within bounds of the document.
        Also updates the cursor in the original document.
        '''
        pass

    def getyx(self):
        "Return the cursor location as (y,x)"
        return (self.y, self.x)

    def addch(self, c):
        '''
        Insert a character at the current cursor location. Ignores
        non-printable characters.
        '''
        pass

    def addstr(self, str):
        "Insert a string at the current cursor location. Handles newline chars."
        pass
