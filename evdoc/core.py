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

    def getyx(self):
        "Return the cursor location as (y,x)"
        return (self.y, self.x)

    def move(self, y, x):
        "Set the cursor location. Will keep cursor within bounds of the document."
        self.y = max(0, min(y, self.max_y()))
        self.x = max(0, min(x, self.max_x()))

    def move_up(self):
        "Move the cursor up, if possible"
        self.move(self.y-1, self.x)

    def move_down(self):
        "Move the cursor down, if possible"
        self.move(self.y+1, self.x)

    def move_left(self):
        "Move the cursor left, if possible"
        if self.x > 0:
            self.move(self.y, self.x-1)
        elif self.y > 0:
            self.move(self.y-1, self.x)
            self.move(self.y, self.max_x())

    def move_right(self):
        "Move the cursor right, if possible"
        if self.x < self.max_x():
            self.move(self.y, self.x+1)
        elif self.y < self.max_y():
            self.move(self.y+1, 0)

    def max_y(self):
        "Return the highest value for y for the cursor"
        return max(0, len(self.lines) - 1)

    def max_x(self):
        "Return the highest value for x for the cursor on the current line"
        return len(self.lines[self.y]) if len(self.lines) > 0 else 0

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

    def backspace(self):
        "Delete the character to the left of the cursor"
        if self.x == 0:
            if self.y != 0:
                new_x = len(self.lines[self.y-1])
                new_y = self.y-1
                self.lines[self.y-1] += self.lines[self.y]
                self.lines = self.lines[:self.y] + self.lines[self.y+1:]
                self.move(new_y, new_x)
        else:
            s = self.lines[self.y]
            self.lines[self.y] = s[:self.x-1] + s[self.x:]
            self.x -= 1

    def delete(self):
        "Delete the character at the cursor"
        max_y = len(self.lines) - 1
        max_x = len(self.lines[self.y])
        if self.x < max_x:
            s = self.lines[self.y]
            self.lines[self.y] = s[:self.x] + s[self.x+1:]
        elif self.y < max_y:
            self.lines[self.y] += self.lines[self.y+1]
            self.lines = self.lines[:self.y+1] + self.lines[self.y+2:]

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
