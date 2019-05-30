import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Canvas  # , Frame
from tkinter.scrolledtext import ScrolledText
from tkinter.constants import YES  # , BOTH
# import threading

# import time


class TextBoxLineNumbers(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_box = None

    def redraw(self):
        self.delete("all")

        i = self.text_box.index("@0,0")
        while True:
            dline = self.text_box.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum)
            i = self.text_box.index("%s+1line" % i)


class TextBox(ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().config(undo=True)
        events_to_bind = ['<Key>', '<MouseWheel>', '<Return>', '<Control-Home>',
                          '<Button-1>',
                          '<Button-2>', '<Button-3>',
                          '<Button-4>',  # scroll up
                          '<Button-5>',  # scroll down
                          '<Configure>',
                          '<B1-Motion>']
        for event in events_to_bind:
            super().bind(event, self.redraw_line_numbers)

        super().bind("<Control-y>", self.redo)
        super().bind("<Control-Y>", self.redo)
        super().bind("<Control-z>", self.undo)
        super().bind("<Control-Z>", self.undo)

        # self['yscrollcommand'] = self.yscroll
        # self.vbar.config(command=self.yview)
        super().focus_set()  # Set focus to the TextBox

    def undo(self, event=None):
        try:
            super().edit_undo()
        except tk.TclError:  # nothing to undo
            pass
        return "break"

    def redo(self, event=None):
        try:
            super().edit_redo()
        except tk.TclError:  # nothing to redo
            pass
        return "break"

    def yview(self, *args):
        super().yview(*args)
        self.redraw_line_numbers()

    # def yscroll(self, *args):
    #     # super().yview(*args)
    #     print("In yscroll")

    def attach(self, line_numbers):
        self.line_numbers = line_numbers
        self.line_numbers.text_box = self

    def redraw_line_numbers(self, event=None):
        self.after(10, self.line_numbers.redraw)
        # self.line_numbers.redraw()


class LineNumberedTextBox():
    def __init__(self, frame):
        self.text_box = TextBox(frame)
        # self.text_box.vbar.config(command=self.text_box.yview)
        self.line_numbers = TextBoxLineNumbers(frame, width=30, highlightthickness=1, bd=1)
        self.text_box.attach(self.line_numbers)

        self.line_numbers.pack(side="left", fill="y")
        self.text_box.pack(side="right", fill="both", expand=YES)

    def redraw_line_numbers(self):
        self.text_box.redraw_line_numbers()

    def bind(self, acc, fcn):
        self.text_box.bind(acc, fcn)


class ErrorDlg(tk.Toplevel):
    def __init__(self, title, message, detail):
        # tk.Toplevel.__init__(self)
        super().__init__()
        self.details_expanded = False
        self.title(title)
        self.geometry("500x100")
        self.minsize(500, 100)
        self.maxsize(1000, 1000)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        text_frame = tk.Frame(self)
        text_frame.grid(row=1, column=0, padx=(7, 7), pady=(7, 7), sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        ttk.Label(button_frame, text=message).grid(row=0, column=0, columnspan=3, pady=(7, 7), padx=(7, 7), sticky="w")
        ok_button = ttk.Button(button_frame, text="OK", command=self.destroy)
        ok_button.grid(row=1, column=1, sticky="e")
        self.details_button = ttk.Button(button_frame, text="Details >>",
                                         command=self.toggle_details)
        self.details_button.grid(row=1, column=2, padx=(7, 7), sticky="e")

        self.textbox = tk.scrolledtext.ScrolledText(text_frame, height=6)
        self.textbox.insert("1.0", detail)
        self.textbox.config(state="disabled")
        # self.scrollb = tk.Scrollbar(text_frame, command=self.textbox.yview)
        # self.textbox.config(yscrollcommand=self.scrollb.set)

        ok_button.focus_set()
        self.grab_set()  # Make this dialog box modal

    def toggle_details(self):
        curr_x, curr_y = self._get_current_pos()
        if not self.details_expanded:
            self.textbox.grid(row=0, column=0, sticky='nsew')
            # self.scrollb.grid(row=0, column=1, sticky='nsew')
            self.resizable(True, True)
            self.geometry('700x500' + '+' + curr_x + '+' + curr_y)
            self.details_button.config(text="<< Details")
            self.details_expanded = True

        else:
            self.textbox.grid_forget()
            # self.scrollb.grid_forget()
            self.resizable(False, False)
            self.geometry('500x85' + '+' + curr_x + '+' + curr_y)
            self.details_button.config(text="Details >>")
            self.details_expanded = False

    def _get_current_pos(self):
        current_geometry = self.geometry()
        first_plus_ind = current_geometry.index('+')
        pos_xy = current_geometry[(first_plus_ind + 1):].split('+')
        assert(len(pos_xy) == 2)
        return pos_xy[0], pos_xy[1]


class ProgressDlg(tk.Toplevel):
    def __init__(self, progress_obj):
        super().__init__()
        self.progress_obj = progress_obj
        self._create_widgets()
        self.is_visible2 = True

    def _create_widgets(self):
        self.title("Simulation Progress")

        self.label1 = ttk.Label(self, textvariable=self.progress_obj.message1)
        self.label1.grid(row=0, column=0, columnspan=2, padx=(10, 0), pady=(10, 4), sticky="w")

        self.progressbar1 = ttk.Progressbar(self,
                                            mode='determinate',  # indeterminate
                                            variable=self.progress_obj.progress1,
                                            length=500)
        self.progressbar1.grid(row=1, column=0, padx=(10, 10), pady=(0, 10), sticky="nsew")

        self.label2 = ttk.Label(self, textvariable=self.progress_obj.message2)
        self.label2.grid(row=2, column=0, padx=(10, 0), pady=(0, 4), sticky="w")

        self.progressbar2 = ttk.Progressbar(self,
                                            mode='determinate',  # indeterminate
                                            variable=self.progress_obj.progress2,
                                            length=500)
        self.progressbar2.grid(row=3, column=0, padx=(10, 10), pady=(0, 5), sticky="nsew")

        # XXX Address in issue 70
        # self.details_box = tk.scrolledtext.ScrolledText(self, height=10)
        # self.details_box.insert("1.0", "Lots of info...")
        # self.details_box.config(state="disabled")
        # self.details_box.grid(row=4, column=0, padx=(10, 10), pady=(5, 5), sticky="nsew")

        button_frame = tk.Frame(self)
        button_frame.grid(row=5, column=0, padx=(10, 10), pady=(0, 0), sticky="e")

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop)
        self.stop_button.grid(row=0, column=0, padx=(10, 0), pady=(0, 5), sticky="w")
        self.close_button = ttk.Button(button_frame, text="Close", command=self.destroy)
        self.close_button.grid(row=0, column=1, padx=(5, 0), pady=(0, 5), sticky="e")
        self.close_button.config(state=tk.DISABLED)

        # stop_button.focus_set()
        self.grab_set()  # Make this dialog box modal

    def set_title(self, title):
        self.title(title)

    def set_visibility2(self, visible):
        if visible:
            if not self.is_visible2:
                self.progressbar2.grid()
                self.label2.grid()
                self.is_visible2 = True
        else:
            if self.is_visible2:
                self.progressbar2.grid_remove()
                self.label2.grid_remove()
                self.is_visible2 = False

    def stop(self):
        self.progress_obj.stop()
        self.close_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_progress(self, level, fraction_done):
        self.progress_obj.update(level, fraction_done)

    def report1(self, message):
        self.label1.config(text=message)

    def report2(self, message):
        self.label2.config(text=message)

# if __name__ == "__main__":
#     root = tk.Tk()
#
#     frame = Frame(root)
#     lntb = LineNumberedTextBox(frame)
#     frame.pack(side="top", anchor="w", fill=BOTH, expand=YES)
#
#     root.mainloop()
