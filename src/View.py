from .Utils import Callbacks
from .AddTradeDialogWindow import AddTradeDialogWindow
from .WarningWindow import WarningWindow

import tkinter as tk
from tkinter import ttk
from tkinter import StringVar

APP_NAME = "TradingMate"

class View():

    def __init__(self):
        # Local data initialisation
        self.callbacks = {}
        self.create_UI()

# GRAPHICAL DEFINITIONS

    def create_UI(self):
        # Create main window
        self.mainWindow = tk.Tk()
        self.mainWindow.title(APP_NAME)
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.on_close_event)
        self.mainWindow.geometry("1024x600")
        # Define the app menu
        self.create_menu()
        # Create the tab format window
        self.noteBook = ttk.Notebook(self.mainWindow)
        self.noteBook.pack(expand=1, fill="both")
        # Create Share trading Tab
        self.create_share_trading_tab()
        # Create Cryptocurencies Tab
        self.create_crypto_tab()

    def create_menu(self):
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
        editmenu.add_command(label="Add trade...", command=self.display_add_trade_panel)
        self.menubar.add_cascade(label="Edit", menu=editmenu)
        # Menu About
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about_popup)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        # Display the menu
        self.mainWindow.config(menu=self.menubar)

    def create_share_trading_tab(self):
        # Create the main frame container and add it to the notebook as a tab
        self.shareTradingPage = ttk.Frame(self.noteBook)
        self.shareTradingPage.pack(expand=True)
        self.noteBook.add(self.shareTradingPage, text="Shares Trading")

        # Create frame containing buttons on the top row of the frame
        buttonsFrame = ttk.Frame(self.shareTradingPage, relief="groove", borderwidth=1)
        buttonsFrame.pack(fill="x", expand=True, anchor="n")
        # Add buttons for the share trading page
        self.addTradeButton = ttk.Button(buttonsFrame, text="Add Trade...", command=self.display_add_trade_panel)
        self.addTradeButton.pack(side="left", anchor="n", padx=5, pady=5)
        self.autoRefresh = tk.IntVar(value=0)
        self.autoRefreshCheckBox = ttk.Checkbutton(buttonsFrame, text="Auto", variable=self.autoRefresh,
                                            command=self.set_auto_refresh, onvalue=1, offvalue=0)
        self.autoRefreshCheckBox.pack(side="right", anchor="n", padx=5, pady=5)
        self.refreshButton = ttk.Button(buttonsFrame, text="Refresh", command=self.refresh_live_data)
        self.refreshButton.pack(side="right", anchor="n", padx=5, pady=5)

        # Create frame containing portfolio balances below the buttons
        balancesFrame = ttk.Frame(self.shareTradingPage, relief="groove", borderwidth=1)
        balancesFrame.pack(fill="none", expand=True, anchor="n", pady=5)
        # Create four different frames for cash, portfolio, total and profit/loss
        cashFrame = ttk.Frame(balancesFrame)
        cashFrame.pack(side="left", fill="y", anchor="n", padx=20, pady=5)
        cashLabel = ttk.Label(cashFrame, text="Cash:")
        cashLabel.pack(side="top")
        self.cashStringVar = tk.StringVar()
        cashValueLabel = ttk.Label(cashFrame, textvariable=self.cashStringVar)
        cashValueLabel.pack(side="bottom")
        # Portfolio balance frame
        portfolioFrame = ttk.Frame(balancesFrame)
        portfolioFrame.pack(side="left", fill="y", anchor="n", padx=20, pady=5)
        portfolioLabel = ttk.Label(portfolioFrame, text="Portfolio:")
        portfolioLabel.pack(side="top")
        self.portfolioStringVar = tk.StringVar()
        portfolioValueLabel = ttk.Label(portfolioFrame, textvariable=self.portfolioStringVar)
        portfolioValueLabel.pack(side="bottom")
        # Total value balance frame
        totalFrame = ttk.Frame(balancesFrame)
        totalFrame.pack(side="left", fill="both", anchor="n", padx=20, pady=5)
        totalLabel = ttk.Label(totalFrame, text="Total:")
        totalLabel.pack(side="top")
        self.totalStringVar = tk.StringVar()
        totalValueLabel = ttk.Label(totalFrame, textvariable=self.totalStringVar)
        totalValueLabel.pack(side="bottom")
        # profits balance frames
        plFrame = ttk.Frame(balancesFrame)
        plFrame.pack(side="left", fill="both", anchor="n", padx=20, pady=5)
        plLabel = ttk.Label(plFrame, text="P/L:")
        plLabel.pack(side="top")
        self.plStringVar = tk.StringVar()
        plValueLabel = ttk.Label(plFrame, textvariable=self.plStringVar)
        plValueLabel.pack(side="bottom")
        plpcFrame = ttk.Frame(balancesFrame)
        plpcFrame.pack(side="left", fill="both", anchor="n", padx=20, pady=5)
        plpcLabel = ttk.Label(plpcFrame, text="P/L %:")
        plpcLabel.pack(side="top")
        self.plpcStringVar = tk.StringVar()
        plpcValueLabel = ttk.Label(plpcFrame, textvariable=self.plpcStringVar)
        plpcValueLabel.pack(side="bottom")

        # Frame containing the holdings table
        holdingsFrame = ttk.Frame(self.shareTradingPage, relief="groove", borderwidth=1)
        holdingsFrame.pack(fill="x", expand=True, anchor="n")
        # Title label
        currLabel = ttk.Label(holdingsFrame, text="Portfolio")
        currLabel.pack()
        # Create a table for the current data
        self.currentDataTreeView = ttk.Treeview(holdingsFrame)
        self.currentDataTreeView.pack(fill='x')
        self.currentDataTreeView["columns"] = ('amount','open','last','cost','value','pl','pl_pc')
        self.currentDataTreeView.heading("#0", text='Symbol', anchor='w')
        self.currentDataTreeView.heading("amount", text='Amount', anchor='w')
        self.currentDataTreeView.heading("open", text='Open [p]', anchor='w')
        self.currentDataTreeView.heading("last", text='Last [p]', anchor='w')
        self.currentDataTreeView.heading("cost", text='Cost [£]', anchor='w')
        self.currentDataTreeView.heading("value", text='Value [£]', anchor='w')
        self.currentDataTreeView.heading("pl", text='P/L £', anchor='w')
        self.currentDataTreeView.heading("pl_pc", text='P/L %', anchor='w')
        self.currentDataTreeView.column("#0", width=100)
        self.currentDataTreeView.column("amount", width=100)
        self.currentDataTreeView.column("open", width=100)
        self.currentDataTreeView.column("last", width=100)
        self.currentDataTreeView.column("cost", width=100)
        self.currentDataTreeView.column("value", width=100)
        self.currentDataTreeView.column("pl", width=100)
        self.currentDataTreeView.column("pl_pc", width=100)

        # Frame containing the trading history
        logFrame = ttk.Frame(self.shareTradingPage, relief="groove", borderwidth=1)
        logFrame.pack(fill="x", expand=True, anchor="n")
        # Title label
        logLabel = ttk.Label(logFrame, text="Trades History")
        logLabel.pack()
        # Use a Frame as container for the treeview and the scrollbar
        tableFrame = ttk.Frame(logFrame)
        tableFrame.pack(fill="x")
        # Create a table for the trading log
        self.logTreeView = ttk.Treeview(tableFrame)
        self.logTreeView.pack(fill='x', side="left", expand=True)
        self.logTreeView["columns"] = ('action','symbol','amount','price','fee', 'stamp_duty')
        self.logTreeView.heading("#0", text='Date', anchor='w')
        self.logTreeView.heading("action", text='Action', anchor='w')
        self.logTreeView.heading("symbol", text='Symbol', anchor='w')
        self.logTreeView.heading("amount", text='Amount', anchor='w')
        self.logTreeView.heading("price", text='Price [p]', anchor='w')
        self.logTreeView.heading("fee", text='Fee [£]', anchor='w')
        self.logTreeView.heading("stamp_duty", text='Stamp Duty [£]', anchor='w')
        self.logTreeView.column("#0", width=100)
        self.logTreeView.column("action", width=100)
        self.logTreeView.column("symbol", width=100)
        self.logTreeView.column("amount", width=100)
        self.logTreeView.column("price", width=100)
        self.logTreeView.column("fee", width=100)
        self.logTreeView.column("stamp_duty", width=100)
        # Create a scrollbar for the history log
        scrollBar = tk.Scrollbar(tableFrame, orient="vertical", command=self.logTreeView.yview)
        scrollBar.pack(side='right', fill='y')
        self.logTreeView.configure(yscrollcommand=scrollBar.set)
        # Create popup menu for the trade history log
        self.logPopupMenu = tk.Menu(self.logTreeView, tearoff=0)
        self.logPopupMenu.add_command(label="Add trade...", command=self.display_add_trade_panel)
        self.logTreeView.bind("<Button-3>", self.trade_log_popup_menu_event)

    def create_crypto_tab(self):
        self.cryptocurrPage = ttk.Frame(self.noteBook)
        self.noteBook.add(self.cryptocurrPage, text="Cryptocurrencies")
        # TODO cryptocurrencies feature

    def start(self):
        # Start the view thread
        self.mainWindow.mainloop()

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

# EVENTS

    def on_close_event(self):
        # Notify the Controller and close the main window
        self.callbacks[Callbacks.ON_CLOSE_VIEW_EVENT]()
        self.mainWindow.destroy()

    def open_log(self):
        # Open a saved log
        print("TODO: open_log")

    def save_log(self):
        # Save the current log
        print("TODO: save_log")

    def show_about_popup(self):
        # Show the about panel
        WarningWindow(self.mainWindow, "About", "Creator: Alberto Cardellini\nEmail: albe.carde@gmail.com")

    def add_entry_to_log_table(self, logEntry):
        v_date = self.check_none_value(logEntry["date"])
        v_act = self.check_none_value(logEntry["action"])
        v_sym = self.check_none_value(logEntry["symbol"])
        v_am = self.check_none_value(logEntry["amount"])
        v_pri = self.check_none_value(logEntry["price"])
        v_fee = self.check_none_value(logEntry["fee"])
        v_sd = self.check_none_value(logEntry["stamp_duty"])
        self.logTreeView.insert('', 'end', text=v_date, values=(v_act,v_sym,v_am,v_pri,v_fee,v_sd))

    def remove_entry_from_log_table(self, position):
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
                                                            round(holdingData['pl'], 2),
                                                            round(holdingData['pl_pc'], 2)))
                    break
            if not found:
                self.currentDataTreeView.insert('','end',text=holdingSymbol, values=(holdingData['amount'],
                                                                                    round(holdingData['open'], 3),
                                                                                    round(holdingData['last'], 3),
                                                                                    round(holdingData['cost'], 3),
                                                                                    round(holdingData['value'], 3),
                                                                                    round(holdingData['pl'], 2),
                                                                                    round(holdingData['pl_pc'], 2)))

    def check_none_value(self, var):
        valid_var = var
        if var is None:
            valid_var = " "
        return valid_var

    def update_balances(self, balances):
        self.cashStringVar.set(str(round(balances["cash"],2)) + "£")
        self.portfolioStringVar.set(str(round(balances["portfolio"],2)) + "£")
        self.totalStringVar.set(str(round(balances["total"],2)) + "£")
        self.plStringVar.set(str(round(balances["pl"],2)) + "£")
        self.plpcStringVar.set(str(round(balances["pl_pc"],2)) + "%")

    def display_add_trade_panel(self):
        AddTradeDialogWindow(self.mainWindow, self.add_new_trade_from_panel)

    def add_new_trade_from_panel(self, newTrade):
        return self.callbacks[Callbacks.ON_NEW_TRADE_EVENT](newTrade)

    def trade_log_popup_menu_event(self, event):
        self.logPopupMenu.post(event.x_root, event.y_root)

    def refresh_live_data(self):
        # Notify the Controller to request new data
        self.callbacks[Callbacks.ON_MANUAL_REFRESH_EVENT]()


    def set_auto_refresh(self):
        # Disable the Refresh button when AutoRefresh is active
        if self.autoRefresh.get() == 1:
            self.refreshButton.config(state="disabled")
        else:
            self.refreshButton.config(state="enabled")
        # Notify the Controller to activate the auto fetch of live data
        print("TODO set_auto_refresh")
            
