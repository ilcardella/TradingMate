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
    def __init__(self, master, config, save_callback):
        tk.Toplevel.__init__(self)
        self.master = master
        self.config = config
        self.save_cb = save_callback
        self.transient(self.master)
        self.title("Settings")
        self.geometry("+%d+%d" % (self.master.winfo_rootx()+400, self.master.winfo_rooty()+100))
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        self.focus_set()
        self.create_UI()

    def create_UI(self):
        ttk.Label(self, text="Trading log path:").grid(row=0, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Credentials path:").grid(row=1, sticky="w", padx=5, pady=5)

        self.trading_log_string = tk.StringVar()
        #self.trading_log_string.trace_add('write', self.check_data_validity)
        self.e_log_path = ttk.Entry(self, textvariable=self.trading_log_string)
        self.e_log_path.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.credentials_string = tk.StringVar()
        #self.credentials_string.trace_add('write', self.check_data_validity)
        self.e_cred_path = ttk.Entry(self, textvariable=self.credentials_string)
        self.e_cred_path.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.trading_log_string.set(self.config['general']['trading_log_path'])
        self.credentials_string.set(self.config['general']['credentials_filepath'])

        # TODO add button to save and cancel
