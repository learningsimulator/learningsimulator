import threading
import traceback
import os
import platform
import sys
import webbrowser
import pathlib
import output
# import matplotlib
from matplotlib import pyplot as plt

import tkinter as tk
from tkinter import ttk
from tkinter.constants import BOTH, YES, NO, DISABLED
# from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox, filedialog

# import matplotlib.pyplot as plt

from widgets import LineNumberedTextBox, ErrorDlg, ProgressDlg, LicenseDlg, WarningDlg
from parsing import Script
from exceptions import ParseException, EvalException, InterruptedSimulation

from functools import partial

import util
import compute

# matplotlib.use('Agg')

TITLE = "Learning Simulator"
FILETYPES = (('Text files', '*.txt'), ('All files', '*.*'))

ROOTDIR = str(pathlib.Path.home())
SEP = os.path.sep
RECENT_FILES_FILE = ROOTDIR + SEP + ".lesimrf.txt"
NUMBER_OF_RECENT_FILES = 10


def read_recent_files_file():
    try:
        with open(RECENT_FILES_FILE, encoding='utf-8') as f:
            file_contents = f.read()
    except Exception:
        return list()
    file_list = file_contents.split('\n')
    nonempty_files = [f for f in file_list if len(f) > 0]
    return nonempty_files


def write_recent_files_file(list_of_files):
    try:
        with open(RECENT_FILES_FILE, 'wb') as f:
            text = '\n'.join(list_of_files)
            f.write(bytes(text, 'UTF-8'))
    except IOError:
        # XXX Maybe add warning if something fails here (e.g. directory write permissions)
        pass


class Gui():
    def __init__(self):
        self.file_path = None
        self.last_open_folder = None
        self.simulation_data = None  # A ScriptOutput object

        self.script_obj = None

        # className appears (at least) in Ubuntu sidebar "tooltip" (app name)
        self.root = tk.Tk(className=TITLE)

        self.progress = None

        self.root.style = ttk.Style()
        self.root.style.theme_use("alt")  # ('clam', 'alt', 'default', 'classic')

        self.set_title()

        self.scriptLabel = None
        self.scriptField = None
        self._create_widgets()
        self._bind_accelerators()

        # Set icon
        icon_file = util.resource_path('Lemur-icon.gif')
        img = tk.PhotoImage(file=icon_file)
        self.root.tk.call('wm', 'iconphoto', self.root._w, img)

        self.root.minsize(width=500, height=600)

        self.root.protocol("WM_DELETE_WINDOW", self.file_quit)

        # When run in bundle, display licene dialog box
        is_bundle = getattr(sys, 'frozen', False)
        if is_bundle:
            LicenseDlg(self)

        self.root.mainloop()
        self.root.quit()

    def _add_recent_file(self, file_to_add):
        current_list = read_recent_files_file()
        if file_to_add in current_list:
            new_list = [file_to_add] + [file for file in current_list if file != file_to_add]
        else:
            new_list = [file_to_add] + current_list
        if len(new_list) > NUMBER_OF_RECENT_FILES:
            new_list = new_list[0: NUMBER_OF_RECENT_FILES]
        write_recent_files_file(new_list)
        self._update_recent_files_menu(new_list)

    def _update_recent_files_menu(self, new_list=None, init=False):
        if new_list is None:
            new_list = read_recent_files_file()
        self._create_recent_files_menu(init)
        for recent_file in new_list:
            lbl = recent_file.replace('/', SEP)
            self.recent_files_menu.add_command(label=lbl, command=partial(self.file_open_recent, recent_file))
        self.recent_files_menu.add_separator()
        self.recent_files_menu.add_command(label="Clear Items", command=self.clear_recent_files)

    def clear_recent_files(self):
        write_recent_files_file(list())
        self._update_recent_files_menu()

    def _create_recent_files_menu(self, init=False):
        OPEN_RECENT = "Open Recent"
        if not init:
            self.file_menu.delete(OPEN_RECENT)
        self.recent_files_menu = tk.Menu(self.file_menu, tearoff=0)
        self.file_menu.insert_cascade(2, label=OPEN_RECENT, menu=self.recent_files_menu,
                                      underline=0)

    def _create_widgets(self):
        # The frame containing the widgets
        frame = tk.Frame(self.root)

        # The menu bar
        self.menu_bar = tk.Menu(self.root, tearoff=0)

        # The File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)  # tearoff = 0: can't be separated from window
        self.file_menu.add_command(label="New", underline=0, command=self.file_new, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open...", underline=0, command=self.file_open, accelerator="Ctrl+O")

        self._update_recent_files_menu(new_list=None, init=True)

        self.file_menu.add_command(label="Save", underline=0, command=self.file_save, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As...", underline=1, command=self.file_save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", underline=1, command=self.file_quit)
        self.menu_bar.add_cascade(label="File", underline=0, menu=self.file_menu)

        # The Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)  # tearoff = 0: can't be seperated from window
        edit_menu.add_command(label="Undo", underline=0, command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", underline=0, command=self.redo, accelerator="Ctrl+Y")
        self.menu_bar.add_cascade(label="Edit", underline=0, menu=edit_menu)

        # The Run menu
        run_menu = tk.Menu(self.menu_bar, tearoff=0)  # tearoff = 0: can't be seperated from window
        run_menu.add_command(label="Simulate and Plot", underline=0, command=self.simulate_thread, accelerator="F5")
        run_menu.add_command(label="Plot", underline=0, command=self.plot_thread)
        self.menu_bar.add_cascade(label="Run", underline=0, menu=run_menu)

        # The Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)  # tearoff = 0: can't be seperated from window
        help_menu.add_command(label="Documentation (offline)", underline=0, command=self.open_documentation_offline,
                              accelerator="F1")
        help_menu.add_command(label="Documentation (online)", underline=0, command=self.open_documentation_online)
        help_menu.add_command(label="License", underline=0, command=self.open_licensedlg)
        self.menu_bar.add_cascade(label="Help", underline=0, menu=help_menu)

        self.root.config(menu=self.menu_bar)

        # The label
        # lbltxt = "Place your script in the box below or open a text file"
        # lbltxt = "Simulate: F5, Open: Ctrl+O, Save: Ctrl+S, New: Ctrl+N"
        # scriptLabel = tk.Label(frame, text=lbltxt)
        # scriptLabel.pack()  # side="top", anchor="w")

        # The LineNumberedTextBox widget
        lntb_frame = tk.Frame(frame)
        self.scriptField = LineNumberedTextBox(lntb_frame)
        lntb_frame.pack(side="top", anchor="w", fill=BOTH, expand=YES)

        # XXX
        # self.scriptField.text_box.insert(1.0, """mechanism: ga
        # stimulus_elements: e1, e2
        # behaviors: b1, b2
        # @PHASE phase1 stop:e1=10
        # L1 e1 | L2
        # L2 e2 | L1
        # @run phase1
        # @vplot e1->b1""")
        # End XXX

        # The Quit button
        # quitButton = tk.Button(frame, text="Quit", command=self.quit)
        # quitButton.pack(side="right")

        button_frame = tk.Frame(frame)

        # The Close All button
        closefigButton = ttk.Button(button_frame, text="Close Figures", command=self.close_figs)
        closefigButton.pack(side="right")

        # The Simulate button
        self.simButton = ttk.Button(button_frame, text="Simulate and Plot",
                                    command=self.simulate_thread)
        self.simButton.pack(side="left")

        # The Plot button
        self.plotButton = ttk.Button(button_frame, text="Plot", command=self.plot_thread)
        self.plotButton.pack(side="left")

        button_frame.pack(side="top", anchor="w", fill=BOTH, expand=NO)
        # button_frame.pack_propagate(False)

        # The message log field
        self.msgField = tk.scrolledtext.ScrolledText(frame, height=2)
        self.msgField.insert(1.0, "Welcome to Learning Simulator!\nThis is the message log.")
        self.msgField.pack(side="top", anchor="w", fill=BOTH, expand=NO)

        self.msgField.config(
            state=DISABLED,
            borderwidth=3,
            font="{Lucida Sans Typewriter} 10",
            # foreground="green",
            background="gray70",
            # insertbackground="white",  # cursor
            # selectforeground="green",  # selection
            # selectbackground="gray50",  # #008000",
            wrap=tk.WORD,  # use word wrapping
            # width=64,
            # undo=True,  # Tk 8.4
        )

        frame.pack(fill=BOTH, expand=YES)

    def simulate_thread(self, event=None):
        try:
            script = self.scriptField.text_box.get("1.0", "end-1c")
            self.script_obj = Script(script)
            self.script_obj.parse()

            msg = self.script_obj.check_deprecated_syntax()
            if msg is not None:
                WarningDlg(msg)

        except Exception as ex:
            self.handle_exception(ex)
            return

        self.progress = Progress(self.script_obj)
        isMac = platform.system().lower() == "darwin"
        if not isMac:
            self.progress.start()
            # self.start_progress_job = self.root.after(1000, self.progress.start)

        self.simulation_thread = threading.Thread(target=self.simulate)
        self.simulation_thread.daemon = True  # So that the thread dies if main program exits

        # The Order of the next two lines matters: simulation.py:Run.run()
        # stops if the compute.stop threading.Event is set
        compute.stop.clear() 
        self.simulation_thread.start()

        self.check_job = self.root.after(100, self.handle_simulation_end)

    def handle_simulation_end(self):
        if self.progress.done:
            assert(not self.simulation_thread.is_alive())
            self.simulation_thread.join()
            self.root.after_cancel(self.check_job)
            if self.progress.exception is not None:
                if not isinstance(self.progress.exception, InterruptedSimulation):
                    self.progress.close_dlg()
                    self.handle_exception(self.progress.exception, self.progress.exception_traceback)
            else:
                # This will also close the progress dialog box
                try:
                    self.script_obj.plot(progress=self.progress)
                except Exception as ex:
                    self.progress.close_dlg()
                    self.handle_exception(ex, traceback.format_exc())
        elif self.progress.stop_clicked:
            compute.stop.set() # stops simulation.py:Run.run()
        else:
            assert(self.simulation_thread.is_alive())
            self.update_progress()
            self.check_job = self.root.after(100, self.handle_simulation_end)

    def update_progress(self):
        if not self.progress:
            return
        while not self.progress.stop_clicked and not compute.progress_queue.empty():
            message = compute.progress_queue.get()
            method = getattr( self.progress, message[0] )
            if len(message)>1:
                method( message[1] )
            else:
                method()

    def simulate(self):
        try:
            compute.worker_queue.put( self.script_obj )
            result = compute.worker_queue.get()
            if type( result[0] ) is output.ScriptOutput:
                self.simulation_data = result[0]
                self.script_obj.postproc(self.simulation_data, self.progress)
            else:
                self.progress.exception = result[0]
                self.progress.exception_traceback = result[1]
        except Exception as ex:
            self.progress.exception = ex
            self.progress.exception_traceback = traceback.format_exc()
        
        self.progress.set_done(True)

    def _select_line(self, lineno):
        start = f"{lineno}.0"
        end = f"{lineno}.{tk.END}"
        self.scriptField.text_box.tag_add(tk.SEL, start, end)

    def enable_simulation_controls(self, enable=True):
        state = "normal"
        if not enable:
            state = DISABLED
        self.simButton.config(state=state)
        self.plotButton.config(state=state)
        self.menu_bar.entryconfig("Run", state=state)

    def plot_thread(self):
        try:
            if self.simulation_data is None:
                raise Exception("No simulation data to plot.")

            script = self.scriptField.text_box.get("1.0", "end-1c")
            self.script_obj = Script(script)
            self.script_obj.parse()
        except Exception as ex:
            self.handle_exception(ex)
            return

        self.progress = Progress(self.script_obj)
        self.progress.start()
        # self.start_progress_job = self.root.after(1000, self.progress.start)

        self.simulation_thread = threading.Thread(target=self.plot)
        self.simulation_thread.daemon = True  # So that the thread dies if main program exits
        self.simulation_thread.start()
        self.check_job = self.root.after(100, self.handle_simulation_end)

    def plot(self):
        try:
            self.script_obj.postproc(self.simulation_data, self.progress)
        except Exception as ex:
            self.progress.exception = ex
            self.progress.exception_traceback = traceback.format_exc()
        finally:
            self.progress.set_done(True)

    def close_figs(self):
        plt.close("all")

    def handle_exception(self, ex, stack_trace=None):
        if isinstance(ex, ParseException):
            if ex.lineno is not None:
                self._select_line(ex.lineno)
        # self.close_figs()  # Fix for issue #83. If ok, remove this line

        err_msg = str(ex)
        if err_msg.startswith("[Errno "):
            rindex = err_msg.index("] ")
            err_msg = err_msg[(rindex + 2):]
        elif (not isinstance(ex, ParseException)) and (not isinstance(ex, EvalException)):
            err_msg = type(ex).__name__ + ": " + err_msg  # Prepend e.g. "KeyError: "

        if stack_trace is None:
            stack_trace = traceback.format_exc()
        ErrorDlg("Error", err_msg, stack_trace)

    def handle_exception_old(self, ex):
        # err_msg = ex.args[0]
        err_msg = str(ex)
        # if len(ex.args) == 2:
        #     err_msg = "{0} {1}".format(err_msg, ex.args[1])
        #     # err_msg = err_msg + ex.args[1]
        messagebox.showerror("Error", err_msg)

    # def file_open(self):
    #     filename = filedialog.askopenfilename()
    #     # filename = "C:/Python/Python36-32/_Markus/scriptexempel2.txt"  # XXX
    #     file = open(filename, "r")
    #     self.scriptField.delete("1.0", "end-1c")
    #     self.scriptField.insert("1.0", file.read())
    #     self.scriptField.mark_set("insert", "1.0")
    #     file.close()  # Make sure you close the file when done

    def save_changes(self):
        if self.scriptField.text_box.edit_modified():
            msg = "This document has been modified. Do you want to save changes?"
            save_changes = messagebox.askyesnocancel("Save?", msg)
            if save_changes is None:  # Cancel
                return False
            elif save_changes is True:  # Yes
                self.file_save()
        return True

    def file_new(self, event=None):
        save_changes = self.save_changes()
        if not save_changes:
            return
        self.scriptField.text_box.delete(1.0, "end")
        self.scriptField.text_box.edit_modified(False)
        self.scriptField.text_box.edit_reset()
        self.file_path = None
        self.set_title()

    def file_open_recent(self, recent_file):
        self._fill_textbox(recent_file)
        self._add_recent_file(recent_file)

    def file_open(self, event=None):
        save_changes = self.save_changes()
        if not save_changes:
            return

        if self.last_open_folder is None:
            initialdir = '.'
        else:
            initialdir = self.last_open_folder

        filepath = filedialog.askopenfilename(filetypes=FILETYPES, initialdir=initialdir)
        if filepath is not None and len(filepath) != 0:
            self._fill_textbox(filepath)
            self._add_recent_file(filepath)

    def _fill_textbox(self, filepath):
        try:
            with open(filepath, encoding='utf-8') as f:
                file_contents = f.read()
        except UnicodeDecodeError:
            # with open(filepath, encoding='utf-8', errors='ignore') as f:
            with open(filepath, encoding='utf-16') as f:
                file_contents = f.read()
        except FileNotFoundError as ex:
            self.handle_exception(ex)
            return

        # Set current text to file contents
        self.scriptField.text_box.delete(1.0, "end")
        self.scriptField.text_box.insert(1.0, file_contents)
        self.scriptField.text_box.edit_modified(False)
        self.scriptField.text_box.mark_set("insert", "1.0")
        self.scriptField.text_box.redraw_line_numbers()
        self.file_path = filepath
        self.last_open_folder = os.path.dirname(filepath)
        self.set_title()

    def file_open_textbox(self, event=None):
        """
        To override default behavior of <Control-O> which inserts a new line in the textbox.
        """
        self.file_open(event)
        return "break"

    def file_save(self, event=None):
        self.file_save_as(filepath=self.file_path)

    def file_save_as(self, filepath=None, event=None):
        if filepath is None:
            filepath = filedialog.asksaveasfilename(filetypes=FILETYPES)
            if len(filepath) == 0:  # Empty tuple or empty string is returned if cancelled
                return  # "cancelled"
            else:
                if ('.' not in filepath) and (not filepath.endswith(".txt")):
                    filepath = filepath + ".txt"
        try:
            with open(filepath, 'wb') as f:
                text = self.scriptField.text_box.get(1.0, "end-1c")
                f.write(bytes(text, 'UTF-8'))
                self.scriptField.text_box.edit_modified(False)
                self.file_path = filepath
                self.set_title()
                self._add_recent_file(filepath)
                return  # "saved"
        except IOError as e:
            self.handle_exception(e)
            return  # "cancelled"

    def file_quit(self, event=None):
        save_changes = self.save_changes()
        if not save_changes:
            return
        self.close_figs()
        # self.root.destroy()  # sys.exit(0)

        # Workaround for tk bug that clipboard is not appended to os clipboard after app exit
        # (Issue #29)
        self.root.after(200, self.root.destroy)
        self.root.mainloop()

    def set_title(self, event=None):
        if self.file_path is not None:
            # title = os.path.basename(self.file_path)
            title = os.path.abspath(self.file_path)
        else:
            title = "Untitled"
        self.root.title(title + " - " + TITLE)

    def _bind_accelerators(self):
        self.root.bind("<Control-n>", self.file_new)
        self.root.bind("<Control-N>", self.file_new)
        self.root.bind("<Control-o>", self.file_open)
        self.root.bind("<Control-O>", self.file_open)
        self.root.bind("<Control-s>", self.file_save)
        self.root.bind("<Control-S>", self.file_save)

        self.scriptField.bind("<Control-O>", self.file_open_textbox)
        self.scriptField.bind("<Control-o>", self.file_open_textbox)

        # self.root.bind_class("Text", ",<Control-z>", self.undo)
        # self.root.bind_class("Text", ",<Control-Z>", self.undo)
        # self.root.bind_class("Text", ",<Control-y>", self.redo)
        # self.root.bind_class("Text", ",<Control-Y>", self.redo)

        self.root.bind("<F5>", self.simulate_thread)
        self.root.bind("<F1>", self.open_documentation_offline)

    def undo(self, event=None):
        self.scriptField.undo()

    def redo(self, event=None):
        self.scriptField.redo()

    def open_documentation_offline(self, event=None):
        url = f".{SEP}docs{SEP}_build{SEP}html{SEP}index.html"
        webbrowser.open(url, new=True)

    def open_documentation_online(self, event=None):
        url = "https://learningsimulator.readthedocs.io/en/latest/"
        webbrowser.open(url, new=True)

    def open_licensedlg(self):
        LicenseDlg(self, include_agree_buttons=False)


class Progress():
    def __init__(self, script_obj):
        self.script_obj = script_obj

        # self.run_labels = script_obj.script_parser.runs.run_labels
        # self.run_lengths = script_obj.script_parser.runs.get_n_subjects()
        self.nsteps1 = sum(script_obj.script_parser.runs.get_n_subjects())
        self.nsteps1_percent = 100 / self.nsteps1 if self.nsteps1 > 0 else 1

        self.nsteps2 = script_obj.script_parser.runs.get_n_phases()
        self.nsteps2_percent = dict()
        for key in self.nsteps2:
            self.nsteps2_percent[key] = 100 / self.nsteps2[key] if self.nsteps2[key] > 0 else 1

        self.progress1 = tk.DoubleVar()  # From 0 to 100
        self.progress2 = tk.DoubleVar()  # From 0 to 100
        self.progress1.set(0)
        self.progress2.set(0)

        self.message1 = tk.StringVar()
        self.message2 = tk.StringVar()

        # The dialog box for the progress bar
        self.dlg = None

        # Set to True when the Stop button has been clicked
        self.stop_clicked = False

        self.exception = None
        self.exception_traceback = None

        self.done = False

    def start(self):
        self.dlg = ProgressDlg(self)
        if self.script_obj.script_parser.runs.all_runs_have_length(1):
            self.dlg.set_visibility2(False)
        self.set_dlg_visibility(False)
        self.dlg.after(500, self.set_dlg_visibility, True)

    def set_dlg_visibility(self, visibility):
        if visibility:
            if not self.done:  # Don't show dlg if progress is done
                self.dlg.update()
                self.dlg.deiconify()
                self.dlg.grab_set()  # update and/or deiconify seem to "demodularize" self.dlg
        else:
            self.dlg.withdraw()

    def stop(self):
        self.stop_clicked = True

    def set_done(self, done):
        self.done = done

    def close_dlg(self):
        if self.dlg is not None:
            self.dlg.destroy()
            self.dlg = None

    def get_n_runs(self):
        return len(self.nsteps2)

    def increment1(self):
        self.progress1.set(self.progress1.get() + self.nsteps1_percent)

    def increment2(self, run_label):
        if self.nsteps2[run_label] == 1:
            if self.dlg is not None:
                self.dlg.set_visibility2(False)
        else:
            if self.dlg is not None:
                self.dlg.set_visibility2(True)
            self.progress2.set(self.progress2.get() + self.nsteps2_percent[run_label])

    def reset1(self):
        self.progress1.set(0)

    def reset2(self):
        self.progress2.set(0)

    # def _update(self, level, fraction_done):
    #     if level == 1:
    #         self.progress1.set(100 * fraction_done)
    #     elif level == 2:
    #         self.progress2.set(100 * fraction_done)

    def report1(self, message):
        self.message1.set(message)

    def report2(self, message):
        self.message2.set(message)


if __name__ == "__main__":
    Gui()
