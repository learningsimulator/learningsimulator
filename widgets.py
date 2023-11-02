import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter import Canvas  # , Frame
from tkinter.scrolledtext import ScrolledText
from tkinter.constants import YES  # , BOTH
from tkinter import messagebox
import platform
# import threading

# import time


class TextBoxLineNumbers(Canvas):
    def __init__(self, font, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_box = None
        self.font = font

    def redraw(self):
        self.delete("all")

        i = self.text_box.index("@0,0")
        while True:
            dline = self.text_box.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_number = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=line_number, font=self.font)
            i = self.text_box.index("%s+1line" % i)

    def set_font(self, font):
        self.font = font
        self.redraw()


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

    def set_font(self, font):
        super().config(font=font)

    def get_current_font(self):
        font_obj = tkFont.Font(font=self['font']).actual()
        return (font_obj['family'], font_obj['size'])

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
        self.font = self.text_box.get_current_font()
        self.line_numbers = TextBoxLineNumbers(self.font, frame, width=30, highlightthickness=1, bd=1)

        self.text_box.attach(self.line_numbers)

        self.line_numbers.pack(side="left", fill="y")
        self.text_box.pack(side="right", fill="both", expand=YES)

        self.text_box.bind("<Control-plus>", self.increase_fontsize)
        self.text_box.bind("<Control-minus>", self.decrease_fontsize)

    def redraw_line_numbers(self):
        self.text_box.redraw_line_numbers()

    def bind(self, acc, fcn):
        self.text_box.bind(acc, fcn)

    def undo(self, event=None):
        self.text_box.undo()

    def redo(self, event=None):
        self.text_box.redo()

    def increase_fontsize(self, event=None):
        self.font = (self.font[0], self.font[1] + 1)
        self._update_font()

    def decrease_fontsize(self, event=None):
        self.font = (self.font[0], self.font[1] - 1)
        self._update_font()

    def _update_font(self):
        self.text_box.set_font(self.font)
        self.line_numbers.set_font(self.font)
        self.redraw_line_numbers()


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

        lbl = ttk.Label(button_frame, text=message)
        lbl.grid(row=0, column=0, columnspan=3, pady=(7, 7), padx=(7, 7), sticky="w")
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
        isLinux = platform.system().lower() == "linux"
        if isLinux:
            self.wait_visibility()
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
        isLinux = platform.system().lower() == "linux"
        if isLinux:
            self.wait_visibility()
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


class WarningDlg():
    def __init__(self, msg):
        messagebox.showwarning(title="Warning", message=msg)


class LicenseDlg(tk.Toplevel):
    def __init__(self, gui, include_agree_buttons=True):
        super().__init__()
        self.gui = gui
        self.title("License")
        self.geometry("500x100")
        self.minsize(700, 400)
        self.maxsize(1000, 700)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.columnconfigure(0, weight=1)

        lbl_frame = tk.Frame(self)
        lbl_frame.grid(row=0, column=0, sticky="nsew")
        lbl_frame.rowconfigure(0, weight=0)
        lbl = ttk.Label(lbl_frame, text=self._get_text(), background=gui.root['bg'])
        lbl.grid(row=0, column=0, pady=(3, 0), padx=(7, 7), sticky="w")

        text_frame = tk.Frame(self)
        text_frame.grid(row=1, column=0, padx=(7, 7), pady=(5, 0), sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        textbox = tk.scrolledtext.ScrolledText(text_frame, height=6)
        textbox.config(wrap=tk.WORD)
        textbox.grid(row=0, column=0, sticky='nsew')
        textbox.insert("1.0", self._get_license_text())
        textbox.config(state="disabled")

        question_frame = tk.Frame(self)
        question_frame.grid(row=2, column=0, padx=(7, 7), pady=(7, 7), sticky="nsew")
        question_frame.columnconfigure(0, weight=1)
        question = ttk.Label(question_frame, text="Do you agree to these terms and conditions?",
                             background=gui.root['bg'])
        question.grid(row=0, column=0, padx=(0, 7), sticky="w")

        button_frame = tk.Frame(question_frame)
        button_frame.grid(row=0, column=1, sticky="e")
        yes_button = ttk.Button(button_frame, text="Yes", command=self.destroy)
        yes_button.grid(row=0, column=0)
        no_button = ttk.Button(button_frame, text="No", command=self.no)
        no_button.grid(row=0, column=1, padx=(5, 0))

        self.resizable(True, True)
        isLinux = platform.system().lower() == "linux"
        if isLinux:
            self.wait_visibility()
        self.grab_set()  # Make this dialog box modal
        if include_agree_buttons:
            yes_button.focus_set()
            self.protocol("WM_DELETE_WINDOW", self.no)
        else:
            question.grid_remove()
            no_button.grid_remove()
            yes_button.config(text="Close")

    @staticmethod
    def _get_text():
        return """Learning Simulator is developed at Centre for Cultural Evolution at Stockholm University.
When using this software in research, please cite it as
    Jonsson, Ghirlanda, Lind, Vinken, Enquist, Learning Simulator: A simulation software for animal
    and human learning, Journal of Open Source Software 6 (2021), no. 58, 2891.

The souce code for this software is hosted on GitHub under the MIT license stated below. It is
built using
- Python(R) (Copyright © 2001-2023 Python Software Foundation (PSF); All Rights Reserved)
- Matplotlib (Copyright © 2012-2023 Matplotlib Development Team (MDT); All Rights Reserved)

The terms and conditions for these products can be found below."""

    @staticmethod
    def _get_license_text():
        return """MIT License for Learning Simulator
----------------------------------
Copyright (c) 2018 learningsimulator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Terms and conditions for accessing or otherwise using Python
------------------------------------------------------------
PSF LICENSE AGREEMENT FOR PYTHON 3.8.2rc2

1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and
   the Individual or Organization ("Licensee") accessing and otherwise using Python
   3.8.2rc2 software in source or binary form and its associated documentation.

2. Subject to the terms and conditions of this License Agreement, PSF hereby
   grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
   analyze, test, perform and/or display publicly, prepare derivative works,
   distribute, and otherwise use Python 3.8.2rc2 alone or in any derivative
   version, provided, however, that PSF's License Agreement and PSF's notice of
   copyright, i.e., "Copyright © 2001-2020 Python Software Foundation; All Rights
   Reserved" are retained in Python 3.8.2rc2 alone or in any derivative version
   prepared by Licensee.

3. In the event Licensee prepares a derivative work that is based on or
   incorporates Python 3.8.2rc2 or any part thereof, and wants to make the
   derivative work available to others as provided herein, then Licensee hereby
   agrees to include in any such work a brief summary of the changes made to Python
   3.8.2rc2.

4. PSF is making Python 3.8.2rc2 available to Licensee on an "AS IS" basis.
   PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED.  BY WAY OF
   EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR
   WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE
   USE OF PYTHON 3.8.2rc2 WILL NOT INFRINGE ANY THIRD PARTY RIGHTS.

5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON 3.8.2rc2
   FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS A RESULT OF
   MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON 3.8.2rc2, OR ANY DERIVATIVE
   THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material breach of
   its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any relationship
   of agency, partnership, or joint venture between PSF and Licensee.  This License
   Agreement does not grant permission to use PSF trademarks or trade name in a
   trademark sense to endorse or promote products or services of Licensee, or any
   third party.

8. By copying, installing or otherwise using Python 3.8.2rc2, Licensee agrees
   to be bound by the terms and conditions of this License Agreement.


License agreement for matplotlib 3.1.3
--------------------------------------
1. This LICENSE AGREEMENT is between the Matplotlib Development Team ("MDT"), and the Individual or Organization ("Licensee") accessing and otherwise using matplotlib software in source or binary form and its associated documentation.

2. Subject to the terms and conditions of this License Agreement, MDT hereby grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative works, distribute, and otherwise use matplotlib 3.1.3 alone or in any derivative version, provided, however, that MDT's License Agreement and MDT's notice of copyright, i.e., "Copyright (c) 2012-2013 Matplotlib Development Team; All Rights Reserved" are retained in matplotlib 3.1.3 alone or in any derivative version prepared by Licensee.

3. In the event Licensee prepares a derivative work that is based on or incorporates matplotlib 3.1.3 or any part thereof, and wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in any such work a brief summary of the changes made to matplotlib 3.1.3.

4. MDT is making matplotlib 3.1.3 available to Licensee on an "AS IS" basis. MDT MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, MDT MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF MATPLOTLIB 3.1.3 WILL NOT INFRINGE ANY THIRD PARTY RIGHTS.

5. MDT SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF MATPLOTLIB 3.1.3 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING MATPLOTLIB 3.1.3, OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint venture between MDT and Licensee. This License Agreement does not grant permission to use MDT trademarks or trade name in a trademark sense to endorse or promote products or services of Licensee, or any third party.

8. By copying, installing or otherwise using matplotlib 3.1.3, Licensee agrees to be bound by the terms and conditions of this License Agreement.
"""

    def no(self):
        self.gui.file_quit()
