import tkinter as tk
import tkinter.ttk as ttk


class topErrorWindow(tk.Toplevel):
    def __init__(self, title, message, detail):
        # tk.Toplevel.__init__(self)
        super().__init__()
        self.details_expanded = False
        self.title(title)
        self.geometry("350x75")
        self.minsize(350, 75)
        self.maxsize(700, 500)
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
        ttk.Button(button_frame, text="OK", command=self.destroy).grid(row=1, column=1, sticky="e")
        self.details_button = ttk.Button(button_frame, text="Details >>",
                                         command=self.toggle_details)
        self.details_button.grid(row=1, column=2, padx=(7, 7), sticky="e")

        self.textbox = tk.scrolledtext.ScrolledText(text_frame, height=6)
        self.textbox.insert("1.0", detail)
        self.textbox.config(state="disabled")
        # self.scrollb = tk.Scrollbar(text_frame, command=self.textbox.yview)
        # self.textbox.config(yscrollcommand=self.scrollb.set)

        self.grab_set()  # Make this dialog box modal

    def toggle_details(self):
        curr_x, curr_y = self._get_current_pos()
        if not self.details_expanded:
            self.textbox.grid(row=0, column=0, sticky='nsew')
            # self.scrollb.grid(row=0, column=1, sticky='nsew')
            self.resizable(True, True)
            self.geometry('350x160' + '+' + curr_x + '+' + curr_y)
            self.details_button.config(text="<< Details")
            self.details_expanded = True

        else:
            self.textbox.grid_forget()
            # self.scrollb.grid_forget()
            self.resizable(False, False)
            self.geometry('350x75' + '+' + curr_x + '+' + curr_y)
            self.details_button.config(text="Details >>")
            self.details_expanded = False

    def _get_current_pos(self):
        current_geometry = self.geometry()
        first_plus_ind = current_geometry.index('+')
        pos_xy = current_geometry[(first_plus_ind + 1):].split('+')
        assert(len(pos_xy) == 2)
        return pos_xy[0], pos_xy[1]


class topErrorWindow_pack(tk.Toplevel):
    def __init__(self, title, message, detail):
        # tk.Toplevel.__init__(self)
        super().__init__()
        self.details_expanded = False
        self.title(title)

        frame1 = tk.Frame(self, width=100, height=100, background="bisque")
        frame1.pack_propagate(0)
        label1 = ttk.Label(frame1, text=message)
        label1.pack()
        #frame2 = tk.Frame(self, width=50, height = 50, background="#b22222")

        frame1.pack(fill=None, expand=False)
        #frame2.place(relx=.5, rely=.5, anchor="c")


        button_frame = tk.Frame(self)
        message_label = ttk.Label(button_frame, text=message)
        message_label.pack()

        ok_button = ttk.Button(button_frame, text="OK", command=self.destroy)
        ok_button.pack()

        self.details_button = ttk.Button(button_frame, text="Details >>",
                                         command=self.toggle_details)
        self.details_button.pack()
        button_frame.pack(fill=None, expand=False)

        self.text_frame = tk.Frame(self)
        self.textbox = tk.scrolledtext.ScrolledText(self.text_frame, height=6)
        self.textbox.insert("1.0", detail)
        self.textbox.config(state="disabled")
        self.textbox.pack()
        self.text_frame.pack(side="top", anchor="w", fill=tk.constants.BOTH, expand=tk.constants.YES)

        self.grab_set()  # Make this dialog box modal

    def toggle_details(self):
        if self.details_expanded:
            self.geometry("600x400+100+100")
            #self.textbox.config(height=1)
            #self.textbox.pack()
            #self.text_frame.pack()
            #self.textbox.pack_forget()
            self.resizable(False, False)
            self.details_button.config(text="Details >>")
            self.details_expanded = False
        else:
            self.geometry("600x300+100+100")
            #self.textbox.config(height=6)
            #self.textbox.pack()
            self.resizable(True, True)
            self.details_button.config(text="<< Details")
            self.details_expanded = True


class topErrorWindow2(tk.Toplevel):
    def __init__(self, title, message, detail):
        tk.Tk.__init__(self)
        self.details_expanded = False
        self.title(title)
        self.geometry("350x75")
        self.minsize(350, 75)
        self.maxsize(425, 250)
        self.resizable(False, False)
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
        ttk.Button(button_frame, text="OK", command=self.destroy).grid(row=1, column=1, sticky="e")
        ttk.Button(button_frame, text="Details", command=self.toggle_details).grid(row=1, column=2, padx=(7, 7), sticky="e")

        self.textbox = tk.Text(text_frame, height=6)
        self.textbox.insert("1.0", detail)
        self.textbox.config(state="disabled")
        self.scrollb = tk.Scrollbar(text_frame, command=self.textbox.yview)
        self.textbox.config(yscrollcommand=self.scrollb.set)

        self.grab_set()

        self.mainloop()

    def toggle_details(self):
        if not self.details_expanded:
            self.textbox.grid(row=0, column=0, sticky='nsew')
            self.scrollb.grid(row=0, column=1, sticky='nsew')
            self.resizable(True, True)
            self.geometry("350x160")
            self.details_expanded = True

        else:
            self.textbox.grid_forget()
            self.scrollb.grid_forget()
            self.resizable(False, False)
            self.geometry("350x75")
            self.details_expanded = False
