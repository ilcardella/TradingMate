import os
import sys
import inspect
from enum import Enum
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils
from UI.TradingMateClient import TradingMateClient
from UI.DataInterface import DataInterface

APP_NAME = "TradingMate"
assets_dir = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_MAIN_WINDOW_FILE = os.path.join(assets_dir, "main_window_layout.glade")
GLADE_NOTEBOOK_PAGE_FILE = os.path.join(assets_dir, "notebook_page_layout.glade")


class Widgets_ID(Enum):
    MAIN_WINDOW = "main_window"
    NOTEBOOK = "notebook"
    NOTEBOOK_PAGE = "notebook_page_box"


class UIHandler:
    def __init__(self, server):
        self._portfolio_tabs = {}
        self._client = TradingMateClient(server)
        self._data_worker = DataInterface(server, self._update_portfolio_tab)
        self._create_UI()

    def _create_UI(self):
        # Build GTK layout from file
        builder = gtk.Builder()
        builder.add_from_file(GLADE_MAIN_WINDOW_FILE)
        self.main_window = builder.get_object(Widgets_ID.MAIN_WINDOW.value)
        self.main_window.connect("destroy", self._on_close_main_window_event)
        self.notebook = builder.get_object(Widgets_ID.NOTEBOOK.value)

    def _on_close_main_window_event(self, event):
        # Check if there are unsaved chnages before closing the app
        if self._client.unsaved_changes():
            # TODO create GTK confirm window
            raise NotImplementedError()
            # ConfirmWindow(
            #     self.mainWindow,
            #     "Warning",
            #     Messages.UNSAVED_CHANGES.value,
            #     self._confirmed_close_window,
            # )
        else:
            self._confirmed_close_window()

    def _confirmed_close_window(self):
        self._data_worker.shutdown()
        self._data_worker.join()
        self._client.stop()
        gtk.main_quit()

    def _update_portfolio_tab(self, portfolio):
        if portfolio.get_id() not in self._portfolio_tabs.keys():
            self._create_portfolio_tab(portfolio)
        # TODO update the portfolio tab
        print(f"Portfolio {portfolio.get_id()} updated")

    def _create_portfolio_tab(self, portfolio):
        page_builder = gtk.Builder()
        page_builder.add_from_file(GLADE_NOTEBOOK_PAGE_FILE)
        page = page_builder.get_object(Widgets_ID.NOTEBOOK_PAGE.value)
        self.notebook.append_page(page, gtk.Label(portfolio.get_name()))
        self._portfolio_tabs[portfolio.get_id()] = page

    ### Public API

    def start(self):
        self._data_worker.start()
        self.main_window.show_all()
        gtk.main()
