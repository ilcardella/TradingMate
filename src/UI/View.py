import os
import sys
import inspect
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from Utils.Utils import Callbacks, Messages
from .WarningWindow import WarningWindow
from .ShareTradingFrame import ShareTradingFrame

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
        # Create Share trading Tab
        self.create_auto_trading_tab()
        # Create Share trading Tab
        #self.create_strategy_backtest_tab()
        # Create Cryptocurencies Tab
        #self.create_crypto_tab()

    def create_menu(self):
        self.menubar = tk.Menu(self.mainWindow)
        # Menu File
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.on_close_event)
        self.menubar.add_cascade(label="File", menu=filemenu)
        # Menu About
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about_popup)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        # Display the menu
        self.mainWindow.config(menu=self.menubar)

    def create_share_trading_tab(self):
        # Create the main frame container and add it to the notebook as a tab
        self.shareTradingFrame = ShareTradingFrame(self.noteBook)
        self.shareTradingFrame.pack(expand=True)
        self.noteBook.add(self.shareTradingFrame, text="Shares Trading")
        self.shareTradingFrame.set_callback(Callbacks.ON_MANUAL_REFRESH_EVENT, self.on_manual_refresh_event)
        self.shareTradingFrame.set_callback(Callbacks.ON_NEW_TRADE_EVENT, self.on_new_trade_event)
        self.shareTradingFrame.set_callback(Callbacks.ON_SET_AUTO_REFRESH_EVENT, self.set_auto_refresh_event)
        self.shareTradingFrame.set_callback(Callbacks.ON_OPEN_LOG_FILE_EVENT, self.on_open_portfolio_event)
        self.shareTradingFrame.set_callback(Callbacks.ON_SAVE_LOG_FILE_EVENT, self.on_save_portfolio_event)
        self.shareTradingFrame.set_callback(Callbacks.ON_DELETE_LAST_TRADE_EVENT, self.on_delete_last_trade_event)

    def create_auto_trading_tab(self):
        self.autoTradingFrame = AutoTradingFrame(self.noteBook)
        self.autoTradingFrame.pack(expand=True)
        self.noteBook.add(self.autoTradingFrame, text="Auto Trading")
        self.autoTradingFrame.set_callback(Callbacks.ON_START_AUTOTRADING, self.on_start_autotrading)
        self.autoTradingFrame.set_callback(Callbacks.ON_STOP_AUTOTRADING, self.on_stop_autotrading)


    def start(self):
        self.shareTradingFrame.set_auto_refresh()
        # Start the view thread
        self.mainWindow.mainloop()

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

# ******* MAIN WINDOW ***********

    def on_close_event(self):
        # Notify the Controller and close the main window
        self.callbacks[Callbacks.ON_CLOSE_VIEW_EVENT]()
        self.mainWindow.destroy()

    def show_about_popup(self):
        # Show the about panel
        WarningWindow(self.mainWindow, "About", Messages.ABOUT_MESSAGE.value)

# ******* SHARE TRADING FRAME ************

    def on_new_trade_event(self, newTrade):
        return self.callbacks[Callbacks.ON_NEW_TRADE_EVENT](newTrade)

    def on_manual_refresh_event(self):
        # Notify the Controller to request new data
        self.callbacks[Callbacks.ON_MANUAL_REFRESH_EVENT]()

    def reset_view(self, resetHistory=False):
        self.shareTradingFrame.reset_view(resetHistory)

    def update_share_trading_history_log(self, logList):
        for entry in logList:
            self.shareTradingFrame.add_entry_to_log_table(entry)

    def update_share_trading_portfolio_balances(self, cash, holdingsValue, totalValue, pl, pl_perc, holdingPL, holdingPLPC, validity):
        self.shareTradingFrame.update_portfolio_balances(cash, holdingsValue, totalValue, pl, pl_perc, holdingPL, holdingPLPC, validity)

    def update_share_trading_holding(self, symbol, amount, openPrice, lastPrice, cost, value, pl, plPc, validity):
        self.shareTradingFrame.update_share_trading_holding(symbol, amount, openPrice, lastPrice, cost, value, pl, plPc, validity)

    def set_db_filepath(self, filepath):
        self.shareTradingFrame.set_db_filepath(filepath)

    def set_auto_refresh_event(self, value):
        self.callbacks[Callbacks.ON_SET_AUTO_REFRESH_EVENT](value)

    def on_open_portfolio_event(self, filename):
        return self.callbacks[Callbacks.ON_OPEN_LOG_FILE_EVENT](filename)

    def on_save_portfolio_event(self, filename):
        return self.callbacks[Callbacks.ON_SAVE_LOG_FILE_EVENT](filename)

    def on_delete_last_trade_event(self):
        self.callbacks[Callbacks.ON_DELETE_LAST_TRADE_EVENT]()

# ******* CRYPTO CURRENCIES FRAME ************

    def on_start_autotrading(self):
        self.callbacks[Callbacks.ON_START_AUTOTRADING]()

    def on_stop_autotrading(self):
        self.callbacks[Callbacks.ON_STOP_AUTOTRADING]()
