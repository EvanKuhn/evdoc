import curses
import evdoc

#==============================================================================
# The App class contains all low-level UI classes, plus the main runtime loop.
#==============================================================================

class App:
    running = False

    def __init__(self):
        self.layout = evdoc.ui.Layout()
        self.screen = None

    def _start_curses(self):
        "Start curses, and initialize the `screen` class variable"
        if App.running:
            raise StandardError("Curses is already running")
        self.screen = curses.initscr()
        curses.cbreak()
        self.screen.keypad(1)
        App.running = True

    def _stop_curses(self):
        "Stop curses, and deinitialize the `screen` class variable"
        if not App.running:
            raise StandardError("Curses is not running")
        curses.nocbreak()
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
        self.editor.redraw()

    def start(self):
        "Initialize curses, draw the UI, and start the main loop"
        input = ''

        debug = open('debug.log', 'w')

        try:
            # Start curses and initialize all curses-based objects
            self._start_curses()
            self.title  = evdoc.ui.Title(self.layout, self.screen, evdoc.TITLE)
            self.editor = evdoc.ui.Editor(self.layout, self.screen)
            self.prompt = evdoc.ui.Prompt(self.layout, self.screen)
            self.redraw()

            # Run the main loop
            while True:
                #curses.curs_set(0)
                #curses.setsyx(3, 2)

                y, x = curses.getsyx()
                debug.write("cursor location: %d, %d\n" % (y, x))
                debug.flush()

                # Get input
                c = self.editor.getch()
                #if debug:
                #    debug.write("char: " + str(c) + "\n")
                #    debug.write("KEY_UP = " + str(curses.KEY_UP) + "\n")
                #    debug.write(str(c == curses.KEY_UP) + "\n")
                #    debug.flush()
                #text = '' #TODO

                # Parse the character
                # TODO

                # Add the character to the editor
                self.editor.addch(c)

                # Update the UI
                #self.editor.redraw()

        # Ignore keyboard interrupts and exit cleanly
        except KeyboardInterrupt:
            pass

        # For other interrupts, re-raise them so we can debug
        except:
            raise

        # Stop curses before we exit
        finally:
            self.stop()
            debug.close()

    def stop(self):
        "Stop curses and stop the app. You must call this before exiting."
        if evdoc.app.App.running:
            self._stop_curses()
