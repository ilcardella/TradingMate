import os
import sys
import inspect
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils
from UI.TradingMateClient import TradingMateClient
from UI.DataInterface import DataInterface
from .PortfolioPage import PortfolioPage

# Application constants
APP_NAME = "TradingMate"
# Filepaths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_MAIN_WINDOW_FILE = os.path.join(ASSETS_DIR, "main_window_layout.glade")
# GTK Widget IDs
MAIN_WINDOW = "main_window"
NOTEBOOK = "notebook"
OPEN_BUTTON = "open_button"
SETTINGS_BUTTON = "settings_button"


class UIHandler:
    def __init__(self, server):
        self._portfolio_tabs = {}
        self._client = TradingMateClient(server)
        self._data_worker = DataInterface(server, self._create_update_portfolio_tab)
        self._create_UI()

    def _create_UI(self):
        # Load GTK layout from file
        builder = gtk.Builder()
        builder.add_from_file(GLADE_MAIN_WINDOW_FILE)
        # Get reference of each widget in the main window and link their callbacks
        self._main_window = builder.get_object(MAIN_WINDOW)
        self._main_window.connect("destroy", self._on_close_main_window_event)
        open_button = builder.get_object(OPEN_BUTTON)
        open_button.connect("clicked", self._on_open_portfolio_event)
        settings_button = builder.get_object(SETTINGS_BUTTON)
        settings_button.connect("clicked", self._on_open_settings_event)
        # TODO add about button
        self.notebook = builder.get_object(NOTEBOOK)

    def _on_close_main_window_event(self, widget):
        # Check if there are unsaved chnages before closing the app
        if self._client.unsaved_changes():
            # TODO create GTK confirm window
            raise NotImplementedError()
            # ConfirmWindow(
            #     self.mainWindow,
            #     "Warning",
            #     Messages.UNSAVED_CHANGES.value,
            #     self._close_application,
            # )
        else:
            self._close_application()

    def _close_application(self):
        self._data_worker.shutdown()
        self._data_worker.join()
        self._client.stop()
        gtk.main_quit()

    def _create_update_portfolio_tab(self, portfolio):
        if portfolio.get_id() not in self._portfolio_tabs.keys():
            self._create_portfolio_tab(portfolio)
        self._portfolio_tabs[portfolio.get_id()].update_data(portfolio)

    def _create_portfolio_tab(self, portfolio):
        # Create a new PortfolioPage and add it to the notebook
        page = PortfolioPage(self._main_window, portfolio.get_id(), self._client)
        self.notebook.append_page(page.get_top_level(), gtk.Label(portfolio.get_name()))
        # TODO can this be just a set() containing the ids?
        self._portfolio_tabs[portfolio.get_id()] = page

    def _on_open_portfolio_event(self, widget):
        try:
            dialog = gtk.FileChooserDialog(
                "Select file",
                self._main_window,
                gtk.FileChooserAction.OPEN,
                (
                    gtk.STOCK_CANCEL,
                    gtk.ResponseType.CANCEL,
                    gtk.STOCK_OPEN,
                    gtk.ResponseType.OK,
                ),
            )
            filter_json = gtk.FileFilter()
            filter_json.set_name("JSON files")
            filter_json.add_mime_type("application/json")
            dialog.add_filter(filter_json)
            response = dialog.run()

            if response == gtk.ResponseType.OK:
                filename = dialog.get_filename()
                if filename is not None and len(filename) > 0:
                    self._client.open_portfolio_event(filename)
            dialog.destroy()
        except RuntimeError as e:
            # TODO Create GTK Warning Window
            # WarningWindow(self.parent, "Warning", e)
            print("WarningWindow")

    def _on_open_settings_event(self, widget):
        config = self._client.get_settings_event()
        print("Settings window")
        # TODO Use GTK Settings Window
        # SettingsWindow(self.mainWindow, config, self._client.save_settings_event)

    ### Public API

    def start(self):
        self._data_worker.start_delayed(2)
        self._main_window.show_all()
        gtk.main()
