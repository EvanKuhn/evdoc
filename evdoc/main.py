import argparse
import curses
import sys
import evdoc

def run():
    "Run the evdoc program"

    # Parse arguments
    parser = argparse.ArgumentParser(
        description = 'evdoc is a console-based document editor, written in Python and curses.',
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-d', '--debug', dest='debug', default=False,
        action='store_true', help='Print debugging output to file debug.log')
    parser.add_argument('--version', dest='version', default=False,
        action='store_true', help='Print the version and exit')
    args = parser.parse_args()

    # Show version?
    if args.version:
        pyver = sys.version_info
        python_version = "%s.%s.%s" % (pyver.major, pyver.minor, pyver.micro)
        print "evdoc version %s (using Python %s, curses %s)" % \
          (evdoc.VERSION, python_version, curses.version)
        sys.exit()

    # Run the app
    app = evdoc.app.App(args)
    app.start()
