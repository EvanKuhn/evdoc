import curses
import evdoc
import os

#==============================================================================
# A simple logger class
#==============================================================================

class Logger(object):
    DEFAULT_FILE = 'debug.log'

    def __init__(self, file=None):
        self.filename = (file if file else self.DEFAULT_FILE)
        self.file = open(self.filename, 'w')

    def log(self, str):
        self.file.write(str + "\n")
        self.file.flush()

    def close(self):
        "Close the log file"
        self.file.close()

#==============================================================================
# A dummy logger class. Does nothing.
#==============================================================================

class DummyLogger(object):
    def __init__(self,):
        pass

    def log(self, str):
        pass

    def close(self):
        pass

#==============================================================================
# The App class contains all low-level UI classes, plus the main runtime loop.
#==============================================================================

def update_status(app):
    doc = app.editor.document
    y, x = doc.getyx()
    if app.editor.scroll_y == 0:
        pct = 'Top'
    elif app.editor.scroll_y + app.layout.editor_rows >= len(doc.lines):
        pct = 'Bot'
    else:
        lines_not_shown = len(doc.lines) - app.layout.editor_rows
        pct = "%d%%" % int(100 * app.editor.scroll_y / lines_not_shown)
    app.status.update(y, x, pct)

class App(object):
    running = False

    def __init__(self, args):
        self.args   = args
        self.logger = evdoc.app.Logger() if args.debug else evdoc.app.DummyLogger()
        self.layout = evdoc.ui.Layout()
        self.screen = None

    def _start_curses(self):
        "Start curses, and initialize the `screen` class variable"
        if App.running:
            raise StandardError("Curses is already running")

        # Fix stupidly long delay on the Escape key
        # http://stackoverflow.com/questions/27372068/
        os.environ.setdefault('ESCDELAY', '25')

        # Now initialize curses
        self.screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.screen.keypad(1)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        App.running = True

    def _stop_curses(self):
        "Stop curses, and deinitialize the `screen` class variable"
        if not App.running:
            raise StandardError("Curses is not running")
        curses.nocbreak()
        curses.echo()
        self.screen.keypad(0)
        self.screen = None
        curses.endwin()
        App.running = False

    def redraw(self):
        "Redraw all windows"
        # Note: the cursor shows up in the last window that is redrawn
        self.title.update()
        self.frame.update()
        self.editor.update()
        self.status.update()
        self.prompt.update()
        curses.doupdate()

    def resize(self):
        "Update the UI based on a terminal resize"
        self.layout.update()
        self.logger.log("Resize to %d x %d" % (self.layout.terminal_cols, self.layout.terminal_rows))
        self.title.resize(self.layout)
        self.status.resize(self.layout)
        self.prompt.resize(self.layout)
        self.frame.resize(self.layout)
        self.editor.resize(self.layout)

    def start(self):
        "Initialize curses, draw the UI, and start the main loop"
        input = ''

        try:
            # Start curses and initialize all curses-based objects
            self._start_curses()
            self.title = evdoc.ui.Title(self.layout, self.logger, evdoc.TITLE)
            self.frame = evdoc.ui.Frame(self.layout, self.logger)
            self.editor = evdoc.ui.Editor(self.layout, self.logger)
            self.editor.set_on_char(update_status, self)
            self.status = evdoc.ui.StatusBar(self.layout, self.logger)
            self.prompt = evdoc.ui.Prompt(self.layout, self.logger)
            self.redraw()

            # Hack: the title isn't showing on startup. A single call to resize
            # fixes that.
            self.resize()

            # Run the main loop
            # TODO: Clean up this while-loop. Too much nesting.
            while True:
                self.editor.focus()
                c = self.editor.edit()

                if c == curses.KEY_RESIZE:
                    self.resize()
                elif c == curses.ascii.ESC:
                    self.prompt.focus()
                    c = self.prompt.edit()
                    if c == curses.KEY_RESIZE:
                        self.resize()
                    elif c == curses.ascii.ESC:
                        pass
                    elif c == curses.ascii.LF:
                        self.logger.log("From prompt: " + self.prompt.contents())
                        self.prompt.clear()

        # Ignore keyboard interrupts and exit cleanly
        except KeyboardInterrupt:
            pass

        # For other interrupts, re-raise them so we can debug
        except:
            raise

        # Stop curses before we exit
        finally:
            self.stop()
            self.logger.close()

    def stop(self):
        "Stop curses and stop the app. You must call this before exiting."
        if evdoc.app.App.running:
            self._stop_curses()
