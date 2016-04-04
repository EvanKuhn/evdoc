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
        self.logfile = open('debug.log', 'w', 0)

    def _start_curses(self):
        "Start curses, and initialize the `screen` class variable"
        if App.running:
            raise StandardError("Curses is already running")
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
        self.editor.redraw()

    def start(self):
        "Initialize curses, draw the UI, and start the main loop"
        input = ''

        try:
            # Start curses and initialize all curses-based objects
            self._start_curses()
            self.title  = evdoc.ui.Title(self.layout, self.screen, evdoc.TITLE)
            self.editor = evdoc.ui.Editor(self.layout, self.screen)
            self.prompt = evdoc.ui.Prompt(self.layout, self.screen)
            self.redraw()

            # Run the main loop
            while True:
                # Get input
                c = self.editor.getch()
                self.log("char: %d\n" % c)

                # Take action
                if c == curses.ascii.LF:
                    self.editor.addch(c)
                    self.editor.redraw()
                elif c == curses.ascii.TAB:
                    pass
                elif curses.ascii.isprint(c):
                    self.editor.addch(c)
                    self.editor.redraw_current_line()
                elif c == curses.KEY_UP:
                    self.editor.move_up()
                elif c == curses.KEY_DOWN:
                    self.editor.move_down()
                elif c == curses.KEY_LEFT:
                    self.editor.move_left()
                elif c == curses.KEY_RIGHT:
                    self.editor.move_right()
                elif c == curses.KEY_RESIZE:
                    self.editor.redraw()
                elif c == curses.ascii.DEL:
                    self.editor.backspace()
                    self.editor.redraw()
                elif c == curses.KEY_DC:
                    self.editor.delete()
                    self.editor.redraw()
                elif c == curses.ascii.ESC:
                    # Get the string from the user, then move back to the editor.
                    self.prompt.reset()
                    curses.echo()
                    s = self.prompt.getstr()
                    curses.noecho()
                    self.prompt.reset()
                    self.editor.redraw()

                # Debug output
                #win_y, win_x = self.editor.window.getyx()
                #doc_y, doc_x = self.editor.document.getyx()
                #self.log("doc: (%d, %d)  win: (%d, %d)\n" % (doc_y, doc_x, win_y, win_x))

        # Ignore keyboard interrupts and exit cleanly
        except KeyboardInterrupt:
            pass

        # For other interrupts, re-raise them so we can debug
        except:
            raise

        # Stop curses before we exit
        finally:
            self.stop()
            self.logfile.close()

    def stop(self):
        "Stop curses and stop the app. You must call this before exiting."
        if evdoc.app.App.running:
            self._stop_curses()

    def log(self, str):
        "Log the string to the debug log file"
        self.logfile.write(str)
        self.logfile.flush()
