# import cProfile

import gui
import parsing

import sys

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
    if not getattr(sys, 'frozen', False):
        assert(args[0].endswith("lesim.py"))
    guiObj = None
    if nargs == 1:
        guiObj = gui.Gui()
    else:
        arg1 = args[1]
        if arg1 == GUI:
            guiObj = gui.Gui()
        elif arg1 == RUN:
            files = args[2:len(args)]
            if len(files) == 0:
                print(
                    "No script file given to lesim run. Type 'lesim.py help' for the available options.".format(arg1))
            nfiles = len(files)
            for i, file in enumerate(files):
                file_obj = open(file, "r")
                script = file_obj.read()
                script_obj = parsing.Script(script)
                script_obj.parse()
                simulation_data = script_obj.run()
                script_obj.postproc(simulation_data)
                block = (i == nfiles - 1)
                script_obj.plot(block)
        elif arg1 == HELP:
            man_page = get_man_page()
            print(man_page)
        else:
            print("Invalid command option '{}' to lesim. Type 'lesim.py help' for the available options.".format(arg1))
