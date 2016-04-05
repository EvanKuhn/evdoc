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
# The App class contains all low-level UI classes, plus the main runtime loop.
#==============================================================================

class App(object):
    running = False

    def __init__(self):
        self.logger = evdoc.app.Logger()
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
        self.screen.refresh()
        self.title.redraw()
        self.prompt.redraw()
        self.frame.redraw()
        self.editor.redraw()

    def resize(self):
        "Update the UI based on a terminal resize"
        self.layout.update()
        self.title.resize(self.layout)
        self.prompt.resize(self.layout)
        self.frame.resize(self.layout)
        self.editor.resize(self.layout)

    def start(self):
        "Initialize curses, draw the UI, and start the main loop"
        input = ''

        try:
            # Start curses and initialize all curses-based objects
            self._start_curses()
            self.title = evdoc.ui.Title(self.layout, evdoc.TITLE)
            self.frame = evdoc.ui.Frame(self.layout)
            self.editor = evdoc.ui.Editor(self.layout, self.logger)
            self.prompt = evdoc.ui.Prompt(self.layout, self.logger)
            self.redraw()

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
