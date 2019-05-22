import threading
import traceback
import os
# import matplotlib
from matplotlib import pyplot as plt

import tkinter as tk
from tkinter import ttk
from tkinter.constants import BOTH, YES, NO, DISABLED
# from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox, filedialog

# import matplotlib.pyplot as plt

from widgets import LineNumberedTextBox, ErrorDlg, ProgressDlg
from parsing import Script
from exceptions import ParseException, InterruptedSimulation

# matplotlib.use('Agg')

TITLE = "Learning Simulator"
FILETYPES = (('Text files', '*.txt'), ('All files', '*.*'))


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
        # self.root.iconbitmap('/home/markus/lesim/lesim2/gui/Lemur-icon.gif')

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        icon_file = curr_dir + '/Lemur-icon.gif'
        img = tk.PhotoImage(file=icon_file)
        self.root.tk.call('wm', 'iconphoto', self.root._w, img)

        self.root.minsize(width=500, height=800)

        self.root.protocol("WM_DELETE_WINDOW", self.file_quit)
        self.root.mainloop()
        self.root.quit()

    def _create_widgets(self):
        # The frame containing the widgets
        frame = tk.Frame(self.root)

        # The menu bar
        self.menu_bar = tk.Menu(self.root, tearoff=0)

        # The File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)  # tearoff = 0: can't be seperated from window
        file_menu.add_command(label="New", underline=0, command=self.file_new, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", underline=0, command=self.file_open, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", underline=0, command=self.file_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", underline=1, command=self.file_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", underline=1, command=self.file_quit)
        self.menu_bar.add_cascade(label="File", underline=0, menu=file_menu)

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
        except Exception as ex:
            self.handle_exception(ex)
            return

        self.progress = Progress(self.root, self.script_obj)
        self.progress.start()
        # self.start_progress_job = self.root.after(1000, self.progress.start)

        self.simulation_thread = threading.Thread(target=self.simulate)
        self.simulation_thread.daemon = True  # So that the thread dies if main program exits
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
                    self.handle_exception(self.progress.exception)
            elif self.progress.done:
                # This will also close the progress dialog box
                self.script_obj.plot(progress=self.progress)
        else:
            assert(self.simulation_thread.is_alive())
            self.check_job = self.root.after(100, self.handle_simulation_end)

    def simulate(self):
        try:
            self.simulation_data = self.script_obj.run(self.progress)
            self.script_obj.postproc(self.simulation_data, progress=self.progress)
        except Exception as ex:
            self.progress.exception = ex
        finally:
            self.progress.set_done(True)
        # return None  # XXX perhaps not needed? for threading

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
            script_obj = Script(script)
            script_obj.parse()
            script_obj.postproc(self.simulation_data)
        except Exception as ex:
            self.handle_exception(ex)
            return

        self.progress = Progress(self.root, self.script_obj)
        self.progress.start()
        # self.start_progress_job = self.root.after(1000, self.progress.start)

        self.simulation_thread = threading.Thread(target=self.plot)
        self.simulation_thread.daemon = True  # So that the thread dies if main program exits
        self.simulation_thread.start()
        self.check_job = self.root.after(100, self.handle_simulation_end)

    def plot(self):
        try:
            if self.simulation_data is None:
                raise Exception("No simulation data to plot.")
            script = self.scriptField.text_box.get("1.0", "end-1c")
            self.script_obj = Script(script)
            self.script_obj.parse()
            self.script_obj.postproc(self.simulation_data)
        except Exception as ex:
            self.handle_exception(ex)

    def close_figs(self):
        plt.close("all")

    def handle_exception(self, ex):
        print(ex)
        if isinstance(ex, ParseException):
            self._select_line(ex.lineno)
        self.close_figs()

        err_msg = str(ex)
        # messagebox.showerror("Error", err_msg)
        st = traceback.format_exc()
        ErrorDlg("Error", err_msg, st)

    def handle_exception_old(self, ex):
        # err_msg = ex.args[0]
        err_msg = str(ex)
        # if len(ex.args) == 2:
        #     err_msg = "{0} {1}".format(err_msg, ex.args[1])
        #     # err_msg = err_msg + ex.args[1]
        messagebox.showerror("Error", err_msg)
        print(traceback.format_exc())

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

    def file_open(self, event=None):  # , filepath=None):
        save_changes = self.save_changes()
        if not save_changes:
            return

        if self.last_open_folder is None:
            initialdir = '.'

            # XXX
            markusdir = '/home/markus/Dropbox/LearningSimulator/Scripts'
            if os.path.isdir(markusdir):
                initialdir = markusdir

        else:
            initialdir = self.last_open_folder

        filepath = filedialog.askopenfilename(filetypes=FILETYPES, initialdir=initialdir)
        if filepath is not None and len(filepath) != 0:
            try:
                with open(filepath, encoding='utf-8') as f:
                    file_contents = f.read()
            except UnicodeDecodeError:
                # with open(filepath, encoding='utf-8', errors='ignore') as f:
                with open(filepath, encoding='utf-16') as f:
                    file_contents = f.read()
            # Set current text to file contents
            self.scriptField.text_box.delete(1.0, "end")
            self.scriptField.text_box.insert(1.0, file_contents)
            self.scriptField.text_box.edit_modified(False)
            self.scriptField.text_box.mark_set("insert", "1.0")
            self.scriptField.text_box.redraw_line_numbers()
            self.file_path = filepath
            self.last_open_folder = os.path.dirname(filepath)
            self.set_title()

        # if event is not None:
        #     try:
        #         self.scriptField.text_box.edit_undo()
        #     except tk.TclError: # Exception:  # as e:
        #         pass  # self.handle_exception(e)

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
        try:
            with open(filepath, 'wb') as f:
                text = self.scriptField.text_box.get(1.0, "end-1c")
                f.write(bytes(text, 'UTF-8'))
                self.scriptField.text_box.edit_modified(False)
                self.file_path = filepath
                self.set_title()
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

    def undo(self):
        self.scriptField.undo()

    def redo(self):
        self.scriptField.redo()


class Progress():
    def __init__(self, tk_obj, script_obj):  # XXX tk_obj?
        self.script_obj = script_obj

        # self.run_labels = script_obj.script_parser.runs.run_labels
        # self.run_lengths = script_obj.script_parser.runs.get_n_subjects()
        self.nsteps1 = sum(script_obj.script_parser.runs.get_n_subjects())
        self.nsteps1_percent = 100 / self.nsteps1

        self.nsteps2 = script_obj.script_parser.runs.get_n_phases()
        self.nsteps2_percent = dict()
        for key in self.nsteps2:
            self.nsteps2_percent[key] = 100 / self.nsteps2[key]

        self.progress1 = tk.DoubleVar()  # tk_obj? # From 0 to 100
        self.progress2 = tk.DoubleVar()  # tk_obj? # From 0 to 100
        self.progress1.set(0)
        self.progress2.set(0)

        self.message1 = tk.StringVar()  # XXX tk_obj?
        self.message2 = tk.StringVar()

        # The dialog box for the progress bar
        self.dlg = None

        # Set to True when the Stop button has been clicked
        self.stop_clicked = False

        self.exception = None

        self.done = False

    def start(self):
        self.dlg = ProgressDlg(self)

    def stop(self):
        self.stop_clicked = True

    def set_done(self, done):
        self.done = done

    def close_dlg(self):
        if self.dlg:
            self.dlg.destroy()
            self.dlg = None

    def get_n_runs(self):
        return len(self.nsteps2)

    def increment1(self):
        self.progress1.set(self.progress1.get() + self.nsteps1_percent)

    def increment2(self, run_label):
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
