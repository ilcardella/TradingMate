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
        self.logTreeView = ttk.Treeview(self.stocksLogPage)
        self.logTreeView.pack(fill='x')
        self.logTreeView["columns"] = ('action','symbol','amount','price','fee')
        self.logTreeView.heading("#0", text='Date', anchor='w')
        self.logTreeView.heading("action", text='Action', anchor='w')
        self.logTreeView.heading("symbol", text='Symbol', anchor='w')
        self.logTreeView.heading("amount", text='Amount', anchor='w')
        self.logTreeView.heading("price", text='Price', anchor='w')
        self.logTreeView.heading("fee", text='Fee', anchor='w')
        self.logTreeView.column("#0", width=100)
        self.logTreeView.column("action", width=100)
        self.logTreeView.column("symbol", width=100)
        self.logTreeView.column("amount", width=100)
        self.logTreeView.column("price", width=100)
        self.logTreeView.column("fee", width=100)
        # Create a table for the current data
        self.currentDataTreeView = ttk.Treeview(self.stocksLogPage)
        self.currentDataTreeView.pack(fill='x')
        #TODO finish the table 
        # Create graphical elements
        self.label = tk.Label(self.stocksLogPage, text="")
        self.label.pack()

    def set_close_event_callback(self, callback):
        self.closeEventCallback = callback

    def on_close_event(self):
        # Notify the Controller and close the main window
        self.closeEventCallback()
        self.mainWindow.destroy()

    def set_log_list(self, aList):
        for logEntry in aList:
            self.logTreeView.insert('', 'end', text=logEntry.get_date(), 
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
