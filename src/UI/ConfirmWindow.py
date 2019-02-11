import os
import sys
import inspect
import tkinter as tk
from tkinter import ttk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

class ConfirmWindow(tk.Toplevel):

    def __init__(self, master, title, message, ok_callback=None, cancel_callback=None):
        tk.Toplevel.__init__(self)
        self.parent = master
        self.message = message
        self.ok_callback = ok_callback
        self.cancel_callback = cancel_callback
        self.transient(self.parent)
        self.title(title)
        self.geometry("+%d+%d" % (self.parent.winfo_rootx()+10, self.parent.winfo_rooty()+10))
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        self.focus_set()

        self.create_UI()

    def create_UI(self):
        ttk.Label(self, text=self.message).grid(row=0, sticky="w", padx=5, pady=5)
        ok_button = ttk.Button(self, text="Ok", command=self.ok)
        ok_button.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
        cancel_button.grid(row=1, column=2, sticky="e", padx=5, pady=5)

        # Make the mas ter thread block execution until this window is closed
        self.parent.wait_window(self)

    def ok(self):
        if self.ok_callback is not None:
            self.ok_callback()
        self.destroy()

    def cancel(self):
        if self.cancel_callback is not None:
            self.cancel_callback()
        self.destroy()
