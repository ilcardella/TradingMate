import os
import sys
import inspect
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from tkinter import filedialog

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Callbacks, Messages, Utils
from .WarningWindow import WarningWindow
from .ConfirmWindow import ConfirmWindow
from .ShareTradingFrame import ShareTradingFrame
from .SettingsWindow import SettingsWindow
from .TradingMateClient import TradingMateClient

APP_NAME = "TradingMate"
assets_dir = os.path.join(Utils.get_install_path(), "data")


class View:
    def __init__(self, server):
        # Local data initialisation
        self._client = TradingMateClient(self, server)
        self._portfolio_tabs = {}
        # Create the user interface
        self._create_UI()

    def _create_UI(self):
        # Create main window
        self.mainWindow = tk.Tk()
        self.mainWindow.title(APP_NAME)
        img = tk.Image("photo", file=assets_dir + "/assets/trading_mate_icon.png")
        self.mainWindow.tk.call("wm", "iconphoto", self.mainWindow._w, img)
        self.mainWindow.protocol("WM_DELETE_WINDOW", self._on_close_main_window_event)
        self.mainWindow.geometry("1024x600")
        # Create the application main menu
        self._create_menu()
        # Create the tab format window
        self.noteBook = ttk.Notebook(self.mainWindow)
        self.noteBook.pack(expand=1, fill="both")

    def _create_menu(self):
        self.menubar = tk.Menu(self.mainWindow)
        # Menu File
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open...", command=self.on_open_portfolio_event)
        filemenu.add_command(label="Settings...", command=self.on_show_settings)
        filemenu.add_command(label="Exit", command=self._on_close_main_window_event)
        self.menubar.add_cascade(label="File", menu=filemenu)
        # Menu About
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self._show_about_popup)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        # Display the menu
        self.mainWindow.config(menu=self.menubar)

    def _create_portfolio_tab(self, portfolio):
        tab = ShareTradingFrame(self.noteBook, portfolio.get_id())
        tab.pack(expand=True)
        tab.set_callback(
            Callbacks.ON_MANUAL_REFRESH_EVENT, self.on_manual_refresh_event
        )
        tab.set_callback(Callbacks.ON_NEW_TRADE_EVENT, self.on_new_trade_event)
        tab.set_callback(
            Callbacks.ON_SET_AUTO_REFRESH_EVENT, self.set_auto_refresh_event
        )
        tab.set_callback(Callbacks.ON_SAVE_LOG_FILE_EVENT, self.on_save_portfolio_event)
        tab.set_callback(Callbacks.ON_SAVE_AS_EVENT, self.on_save_portfolio_as_event)
        tab.set_callback(
            Callbacks.ON_DELETE_LAST_TRADE_EVENT, self.on_delete_last_trade_event
        )
        self.noteBook.add(tab, text=portfolio.get_name())
        self._portfolio_tabs[portfolio.get_id()] = tab
        tab.set_auto_refresh()

    # ******* MAIN WINDOW ***********

    def _on_close_main_window_event(self):
        # Check if there are unsaved chnages before closing the app
        if self._client.unsaved_changes():
            ConfirmWindow(
                self.mainWindow,
                "Warning",
                Messages.UNSAVED_CHANGES.value,
                self._confirmed_close_window,
            )
        else:
            self._confirmed_close_window()

    def _confirmed_close_window(self):
        self._client.stop()
        self.mainWindow.destroy()

    def _show_about_popup(self):
        WarningWindow(self.mainWindow, "About", Messages.ABOUT_MESSAGE.value)

    def start(self):
        """Start the User Interface"""
        # Start thread to fetch data from the server
        self._client.start()
        # Start the user interface thread
        self.mainWindow.mainloop()

    # ******* SHARE TRADING FRAMES ************

    def update_portfolio_tab(self, portfolio):
        """Update the portfolio tab with the recent data"""
        if portfolio.get_id() not in self._portfolio_tabs.keys():
            self._create_portfolio_tab(portfolio)
        # Update history table
        self._portfolio_tabs[portfolio.get_id()].update_trades_log(
            portfolio.get_trade_history()[::-1]
        )
        # Update the current positions
        validity = True
        for h in portfolio.get_holding_list():
            self._portfolio_tabs[portfolio.get_id()].update_share_trading_holding(
                h.get_symbol(),
                h.get_quantity(),
                h.get_open_price(),
                h.get_last_price(),
                h.get_cost(),
                h.get_value(),
                h.get_profit_loss(),
                h.get_profit_loss_perc(),
                h.get_last_price_valid(),
            )
            validity = validity and h.get_last_price_valid()
        # Update the balances
        self._portfolio_tabs[portfolio.get_id()].update_portfolio_balances(
            portfolio.get_cash_available(),
            portfolio.get_holdings_value(),
            portfolio.get_total_value(),
            portfolio.get_portfolio_pl(),
            portfolio.get_portfolio_pl_perc(),
            portfolio.get_open_positions_pl(),
            portfolio.get_open_positions_pl_perc(),
            validity,
        )

    def on_new_trade_event(self, new_trade, portfolio_id):
        try:
            self._client.new_trade_event(new_trade, portfolio_id)
        except RuntimeError as e:
            return {"success": False, "message": e}
        return {"success": True, "message": "ok"}

    def on_manual_refresh_event(self, portfolio_id):
        self._client.manual_refresh_event(portfolio_id)

    def set_auto_refresh_event(self, value, portfolio_id):
        self._client.set_auto_refresh_event(value, portfolio_id)

    def on_open_portfolio_event(self):
        try:
            filename = filedialog.askopenfilename(
                initialdir=Utils.get_install_path(),
                title="Select file",
                filetypes=(("json files", "*.json"), ("all files", "*.*")),
            )
            if filename is not None and len(filename) > 0:
                self._client.open_portfolio_event(filename)
        except RuntimeError as e:
            WarningWindow(self.parent, "Warning", e)

    def on_save_portfolio_event(self, portfolio_id):
        # None forces to save portfolio in its current filepath
        self._client.save_portfolio_event(portfolio_id, None)

    def on_save_portfolio_as_event(self, portfolio_id):
        try:
            filename = filedialog.asksaveasfilename(
                initialdir=Utils.get_install_path(),
                title="Select file",
                filetypes=(("json files", "*.json"), ("all files", "*.*")),
            )
            if filename is not None and len(filename) > 0:
                self._client.save_portfolio_event(portfolio_id, filename)
        except RuntimeError as e:
            WarningWindow(self.parent, "Warning", e)

    def on_delete_last_trade_event(self, portfolio_id):
        try:
            self._client.delete_last_trade_event(portfolio_id)
        except RuntimeError as e:
            return {"success": False, "message": e}
        return {"success": True, "message": "ok"}

    def on_show_settings(self):
        config = self._client.get_settings_event()
        SettingsWindow(self.mainWindow, config, self._client.save_settings_event)
