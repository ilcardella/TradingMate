import tkinter as tk
from tkinter import ttk

class SpreadBettingFrame(tk.Frame):

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
        # TODO