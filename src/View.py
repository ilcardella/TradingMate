from .Utils import Callbacks

import tkinter as tk
from tkinter import ttk
from tkinter import StringVar

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
        filemenu.add_command(label="Open...", command=self.open_log)
        filemenu.add_command(label="Save...", command=self.save_log)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_close_event)
        self.menubar.add_cascade(label="File", menu=filemenu)
        # Menu Edit
        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Add trade...", command=self.add_trade_to_log)
        self.menubar.add_cascade(label="Edit", menu=editmenu)
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
        # Portfolio summary label
        self.balancesString = StringVar()
        self.balancesString.set("[BALANCES] ")
        balancesLabel = ttk.Label(self.stocksLogPage, textvariable=self.balancesString)
        balancesLabel.pack(fill="x")
        # Title label
        currLabel = ttk.Label(self.stocksLogPage, text="Live Price")
        currLabel.pack()        
        # Create a table for the current data
        self.currentDataTreeView = ttk.Treeview(self.stocksLogPage)
        self.currentDataTreeView.pack(fill='x')
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
        # Title label
        logLabel = ttk.Label(self.stocksLogPage, text="Trades History")
        logLabel.pack()
        # Create a table for the trading log
        self.logTreeView = ttk.Treeview(self.stocksLogPage)
        self.logTreeView.pack(fill='x',side='bottom')
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
        v_date = self.check_none_value(date)
        v_act = self.check_none_value(action)
        v_sym = self.check_none_value(symbol)
        v_am = self.check_none_value(amount)
        v_pri = self.check_none_value(price)
        v_fee = self.check_none_value(fee)
        self.logTreeView.insert('', 'end', text=v_date, values=(v_act,v_sym,v_am,v_pri,v_fee))

    def remove_entry_from_log(self, position):
        self.logTreeView.delete(position)

    def update_live_price(self, holdingDict):
        for holdingSymbol in holdingDict.keys():
            holdingData = holdingDict[holdingSymbol]
            found = False
            for child in self.currentDataTreeView.get_children():
                item = self.currentDataTreeView.item(child)
                symbol = item['text']
                if holdingSymbol == symbol:
                    found = True
                    self.currentDataTreeView.item(child, values=(holdingData['amount'],
                                                            round(holdingData['open'], 3),
                                                            round(holdingData['last'], 3),
                                                            round(holdingData['cost'], 3),
                                                            round(holdingData['value'], 3),
                                                            round(holdingData['pl'], 2)))
                    break
            if not found:
                self.currentDataTreeView.insert('','end',text=holdingSymbol, values=(holdingData['amount'],
                                                                                    round(holdingData['open'], 3),
                                                                                    round(holdingData['last'], 3),
                                                                                    round(holdingData['cost'], 3),
                                                                                    round(holdingData['value'], 3),
                                                                                    round(holdingData['pl'], 2)))

    def start(self):
        # Start the view thread
        self.mainWindow.mainloop()

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def check_none_value(self, var):
        valid_var = var
        if var is None:
            valid_var = " "
        return valid_var

    def update_balances(self, balances):
        balString = "[BALANCES] Cash: " + str(balances["cash"]) + "£ - Portfolio: " + str(balances["portfolio"]) + "£ - Total: " + str(balances["total"]) +"£"
        self.balancesString.set(balString)

    def add_trade_to_log(self):
        print("TODO add_trade_to_log")
