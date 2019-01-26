import os
import sys
import inspect
import tkinter as tk
from tkinter import ttk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

class WarningWindow(tk.Toplevel):

    def __init__(self, master, title, message):
        tk.Toplevel.__init__(self)
        self.parent = master
        self.message = message
        self.transient(self.parent)
        self.title(title)
        self.geometry("+%d+%d" % (self.parent.winfo_rootx()+10, self.parent.winfo_rooty()+10))
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        self.focus_set()

        self.create_UI()

    def create_UI(self):
        ttk.Label(self, text=self.message).grid(row=0, sticky="w", padx=5, pady=5)
        button = ttk.Button(self, text="Ok", command=self.destroy)
        button.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Make the mas ter thread block execution until this window is closed
        self.parent.wait_window(self)
