from .Utils import Callbacks

import tkinter as tk
from tkinter import ttk

APP_NAME = "TradingMate"

class View():

    def __init__(self):
        # Local data initialisation
        self.callbacks = {}
        self.create_UI()

    def create_UI(self):
        # Create main window
        self.mainWindow = tk.Tk()
        self.mainWindow.title(APP_NAME)
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.on_close_event)
        self.mainWindow.geometry("1000x500")

        # Define the app menu
        self.menubar = tk.Menu(self.mainWindow)
        # Menu File
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_log)
        filemenu.add_command(label="Save", command=self.save_log)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_close_event)
        self.menubar.add_cascade(label="File", menu=filemenu)
        # Menu About
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about_popup)
        self.menubar.add_cascade(label="Help", menu=helpmenu)

        # Display the menu
        self.mainWindow.config(menu=self.menubar)

        # Create the notebook (tab format window)
        nb = ttk.Notebook(self.mainWindow)
        # Create Share trading Tab
        self.stocksLogPage = ttk.Frame(nb)
        nb.add(self.stocksLogPage, text="Stocks Trading")
        # Create Cryptocurencies Tab
        self.cryptocurrPage = ttk.Frame(nb)
        nb.add(self.cryptocurrPage, text="Cryptocurrencies")
        # Notebook layout definition
        nb.pack(expand=1, fill="both")
        # Title label
        logLabel = ttk.Label(self.stocksLogPage, text="Trades History")
        logLabel.pack()
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
        # Title label
        currLabel = ttk.Label(self.stocksLogPage, text="Live Price")
        currLabel.pack()        
        # Create a table for the current data
        self.currentDataTreeView = ttk.Treeview(self.stocksLogPage)
        self.currentDataTreeView.pack(fill='x',side='bottom')
        self.currentDataTreeView["columns"] = ('amount','open','last','cost','value','pl')
        self.currentDataTreeView.heading("#0", text='Symbol', anchor='w')
        self.currentDataTreeView.heading("amount", text='Amount', anchor='w')
        self.currentDataTreeView.heading("open", text='Open', anchor='w')
        self.currentDataTreeView.heading("last", text='Last', anchor='w')
        self.currentDataTreeView.heading("cost", text='Cost', anchor='w')
        self.currentDataTreeView.heading("value", text='Value', anchor='w')
        self.currentDataTreeView.heading("pl", text='% P/L', anchor='w')
        self.currentDataTreeView.column("#0", width=100)
        self.currentDataTreeView.column("amount", width=100)
        self.currentDataTreeView.column("open", width=100)
        self.currentDataTreeView.column("last", width=100)
        self.currentDataTreeView.column("cost", width=100)
        self.currentDataTreeView.column("value", width=100)
        self.currentDataTreeView.column("pl", width=100)

    def on_close_event(self):
        # Notify the Controller and close the main window
        self.callbacks[Callbacks.ON_CLOSE_VIEW_EVENT]()
        self.mainWindow.destroy()

    def open_log(self):
        print("TODO: open_log")

    def save_log(self):
        print("TODO: save_log")

    def show_about_popup(self):
        print("TODO: show_about_popup")

    def add_entry_to_log(self, date, action, symbol, amount, price, fee):
        self.logTreeView.insert('', 'end', text=date, values=(action,symbol,amount,price,fee))

    def remove_entry_from_log(self, position):
        self.logTreeView.delete(position)

    def update_live_prices(self, dict):
        found = False
        for child in self.currentDataTreeView.get_children():
            item = self.currentDataTreeView.item(child)
            if item['text'] == dict['symbol']:
                found = True
                self.currentDataTreeView.item(child, values=(dict['amount'],
                                                            dict['open'],
                                                            dict['last'],
                                                            dict['cost'],
                                                            dict['value'],
                                                            dict['pl']))
        if not found:
            self.currentDataTreeView.insert('','end',text=dict['symbol'], values=(dict['amount'],
                                                                                    dict['open'],
                                                                                    dict['last'],
                                                                                    dict['cost'],
                                                                                    dict['value'],
                                                                                    dict['pl']))

    def start(self):
        # Start the view thread
        self.mainWindow.mainloop()

    def set_callback(self, id, callback):
        self.callbacks[id] = callback
