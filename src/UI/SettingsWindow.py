import os
import sys
import inspect
import tkinter as tk
from tkinter import ttk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from Utils.Utils import Actions, Markets
from Utils.Trade import Trade
from .WarningWindow import WarningWindow

class SettingsWindow(tk.Toplevel):
    """
    Settings panel window
    """
    def __init__(self, master, save_callback):
        tk.Toplevel.__init__(self)
        self.master = master
        self.save_cb = save_callback
        self.transient(self.master)
        self.title("Settings")
        self.geometry("+%d+%d" % (self.master.winfo_rootx()+400, self.master.winfo_rooty()+100))
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        self.focus_set()
        self.create_UI()

    def create_UI(self):
        pass
