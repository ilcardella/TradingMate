import os
import sys
import inspect
import tkinter as tk
from tkinter import ttk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from Utils.Utils import Callbacks

class AutoTradingFrame(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.callbacks = {}
        self.create_UI()

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def create_UI(self):
        buttonsFrame = ttk.Frame(self, relief="groove", borderwidth=1)
        buttonsFrame.pack(fill="both", expand=True, anchor="n")
        # Add buttons
        startButton = ttk.Button(buttonsFrame, text="Start", command=self.start_auto_trading)
        startButton.pack(side="left", anchor="n", padx=5, pady=5)
        stopButton = ttk.Button(buttonsFrame, text="Stop", command=self.stop_auto_trading)
        stopButton.pack(side="left", anchor="n", padx=5, pady=5)

    def start_auto_trading(self):
        self.callbacks[Callbacks.ON_START_AUTOTRADING]()

    def stop_auto_trading(self):
        self.callbacks[Callbacks.ON_STOP_AUTOTRADING]()
