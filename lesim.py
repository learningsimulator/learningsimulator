import sys
import traceback
import compute

import gui
import cli
import parsing

GUI = "gui"
RUN = "run"
HELP = "help"

def get_man_page():
    return """Help for the Learning Simulator control command lesim.

    python lesim.py
        Short for "python lesim.py gui"

    python lesim.py gui
        Starts the Learning Simulator gui

    python lesim.py run file1 [file2, file3, ...]
        Run the script files file1, file2, ...

    python lesim.py help
        Display this help and exit"""


if __name__ == "__main__":
    args = sys.argv
    nargs = len(args)
    assert(nargs >= 1)
    is_bundle = getattr(sys, 'frozen', False)
    if not is_bundle:
        assert(args[0].endswith("lesim.py"))

    guiObj = None
    if nargs == 1 or (nargs>1 and args[1] == GUI):
        compute.process.start()
        guiObj = gui.Gui()
    elif args[1] == RUN:
        files = args[2:nargs]

        if len(files) == 0:
            print("No script file given to lesim run. Type 'lesim.py help' for the available options.")
            sys.exit(1)
        
        cliObj = cli.Cli( files )

    elif arg1 == HELP:
        man_page = get_man_page()
        print(man_page)
    else:
        print("Invalid command option '{}' to lesim. Type 'lesim.py help' for the available options.".format(arg1))

if compute.process.is_alive():
    compute.process.terminate()
