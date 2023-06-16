import threading
import traceback
import os
import platform
import sys
import webbrowser
import pathlib
import output
import time
# import matplotlib
from matplotlib import pyplot as plt

from parsing import Script
from exceptions import ParseException, EvalException, InterruptedSimulation

import util
import compute

class Cli():
    def __init__(self, files):
        self.simulation_data = None  # A ScriptOutput object
        self.script_obj = None

        nfiles = len(files)
        for i, file in enumerate(files):
            file_obj = open(file, "r")
            script = file_obj.read()
            self.script_obj = Script(script)
            self.script_obj.parse()

            msg = self.script_obj.check_deprecated_syntax()
            if msg is not None:
                print(msg)

            self.progress = Progress(self.script_obj)
            self.progress.start()

            block = (i == nfiles - 1)
            self.simulation_thread = threading.Thread(target=self.simulate)
            self.simulation_thread.daemon = True  # So that the thread dies if main program exits
            self.simulation_thread.start()

            while True: # wait for simulation thread to set self.progress.done
                if self.progress.done:
                    assert(not self.simulation_thread.is_alive()) # should be done
                    self.simulation_thread.join()                 # tidy up
                    if self.progress.exception is not None:       # oops
                        compute.progress_queue.close()            # tidy up
                        print(self.progress.exception_traceback)  # mimic exception
                        print(self.progress.exception)
                        sys.exit(1)
                    else:
                        break
                self.update_progress()
                time.sleep(0.1)                

            self.script_obj.postproc(self.simulation_data, self.progress)
            self.script_obj.plot(block=block, progress=self.progress)

        compute.progress_queue.close()
        print('\033[2K', "Done")

    def update_progress(self):
        if not self.progress:
            return
        while not compute.progress_queue.empty():
            message = compute.progress_queue.get()
            method = getattr( self.progress, message[0] )
            if len(message)>1:
                method( message[1] )
            else:
                method()
            if self.progress.done:
                break
            
    def simulate(self):
        try:
            self.simulation_data = self.script_obj.run()
        except Exception as ex:
            self.progress.exception = ex
            self.progress.exception_traceback = traceback.format_exc()
        
        self.progress.set_done(True)

class Progress():
    def __init__(self, script_obj):
        self.script_obj = script_obj

        # self.run_labels = script_obj.script_parser.runs.run_labels
        # self.run_lengths = script_obj.script_parser.runs.get_n_subjects()
        self.nsteps1 = sum(script_obj.script_parser.runs.get_n_subjects())
        self.nsteps2 = script_obj.script_parser.runs.get_n_phases()

#        for key in self.nsteps2:
#            self.nsteps2_percent[key] = 100 / self.nsteps2[key] if self.nsteps2[key] > 0 else 1

        self.progress1 = 0  # From 0 to 100
        self.progress2 = 0  # From 0 to 100

        self.message1 = ""
        self.message2 = ""

        # Compatibility with gui.Progress
        self.dlg = None
        self.stop_clicked = False

        self.exception = None
        self.exception_traceback = None

        self.done = False

    def start(self):
        pass

    def stop(self):
        self.stop_clicked = True

    def set_done(self, done):
        self.done = done

    def close_dlg(self):
        pass

    def get_n_runs(self):
        return len(self.nsteps2)

    def update(self):
        value1 = round( 100 * self.progress1 / self.nsteps1 )
        if self.message1[0:8] != "Running ":
            prefix = "Running "
        else:
            prefix = ""
        print( '\033[2K', f"{prefix}{self.message1} {value1}%", end="\r" )

    def set1(self, value):
        self.progress1 = value * self.nsteps1 / 100
        self.update()

    def increment1(self):
        self.progress1 += 1
        self.update()

    def increment2(self, run_label):
        pass
        # if self.nsteps2[run_label] == 1:
        #     if self.dlg is not None:
        #         self.message2 = ""
        # else:
        #     self.progress2 = self.progress2.get() + self.nsteps2_percent[run_label]
        # self.update()

    def reset1(self):
        self.progress1 = 0
        self.update()

    def reset2(self):
        self.progress2 = 0
        self.update()

    def report1(self, message):
        self.message1 = message
        self.update()

    def report2(self, message):
        self.message2 = message
        self.update()
