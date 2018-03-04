import tkinter as tk
from tkinter import ttk

APP_NAME = "TradingMate"

class View():

    def __init__(self):
        # Local data initialisation
        self.closeEventCallback = None
        self.create_UI()

    def create_UI(self):
        # Create main window
        self.mainWindow = tk.Tk()
        self.mainWindow.title(APP_NAME)
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.on_close_event)
        self.mainWindow.geometry("1000x500")

        # Create the notebook (tab format)
        nb = ttk.Notebook(self.mainWindow)
        # Create Share trading Tab
        self.stocksLogPage = ttk.Frame(nb)
        nb.add(self.stocksLogPage, text="Stocks Trading")
        # Create Cryptocurencies Tab
        self.cryptocurrPage = ttk.Frame(nb)
        nb.add(self.cryptocurrPage, text="Cryptocurrencies")
        # Notebook layout definition
        nb.pack(expand=1, fill="both")

        # Create a table for the trading log
        tv = ttk.Treeview(self.stocksLogPage)
        tv.pack(fill='x')
        tv["columns"] = ('action','symbol','amount','price','fee')
        tv.heading("#0", text='Date', anchor='w')
        tv.heading("action", text='Action', anchor='w')
        tv.heading("symbol", text='Symbol', anchor='w')
        tv.heading("amount", text='Amount', anchor='w')
        tv.heading("price", text='Price', anchor='w')
        tv.heading("fee", text='Fee', anchor='w')
        tv.column("#0", width=100)
        tv.column("action", width=100)
        tv.column("symbol", width=100)
        tv.column("amount", width=100)
        tv.column("price", width=100)
        tv.column("fee", width=100)
        self.treeView = tv

        # Create graphical elements
        self.label = tk.Label(self.stocksLogPage, text="")
        self.label.pack()
        self.logLabel = tk.Label(self.stocksLogPage, text="")
        self.logLabel.pack()

    def set_close_event_callback(self, callback):
        self.closeEventCallback = callback

    def on_close_event(self):
        # Notify the Controller and close the main window
        self.closeEventCallback()
        self.mainWindow.destroy()

    def set_log_list(self, aList):
        for logEntry in aList:
            self.treeView.insert('', 'end', text=logEntry.get_date(), 
                                values=(logEntry.get_action(), 
                                        logEntry.get_symbol(),
                                        logEntry.get_amount(),
                                        logEntry.get_price(),
                                        logEntry.get_fee()))

    def set_stock_prices(self, aDict):
        self.label.config(text=aDict)

    def start(self):
        # Start the view thread
        self.mainWindow.mainloop()
