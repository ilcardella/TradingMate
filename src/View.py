import tkinter as tk
from tkinter import ttk

APP_NAME = "TradingMate"

class View():

    def __init__(self):
        # Local data struct
        self.logList = []
        self.closeEventCallback = None

        # Create main window
        self.mainWindow = tk.Tk()
        self.mainWindow.title(APP_NAME)
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.on_close_event)
        self.mainWindow.geometry("400x400")

        nb = ttk.Notebook(self.mainWindow) # Tabs format

        # Create Tab1 = Share trading log
        stocksLogPage = ttk.Frame(nb)
        nb.add(stocksLogPage, text="Stocks Trading")

        # Create Tab2 = Crypto log
        cryptocurrPage = ttk.Frame(nb)
        nb.add(cryptocurrPage, text="Cryptocurrencies")

        nb.pack(expand=1, fill="both")

        # Create graphical elements
        self.label = tk.Label(stocksLogPage, text="")
        self.label.grid(column=0,row=1)

        self.logLabel = tk.Label(stocksLogPage, text="")
        self.logLabel.grid(column=0,row=2)

    def set_close_event_callback(self, callback):
        self.closeEventCallback = callback

    def on_close_event(self):
        # 2. Notify the Controller
        self.closeEventCallback()
        # 3. Close the main window
        self.mainWindow.destroy()

    def set_log_list(self, aList):
        self.logList = aList
        self.logLabel.config(text=self.logList[0])

    def set_stock_prices(self, aDict):
        self.label.config(text=aDict)

    def start(self):
        self.mainWindow.mainloop()
