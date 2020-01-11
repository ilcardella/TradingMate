import os
import sys
import inspect
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk, GLib

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils, Messages
from UI.TradingMateClient import TradingMateClient
from UI.DataInterface import DataInterface
from .PortfolioPage import PortfolioPage
from .MessageDialog import MessageDialog
from .ConfirmDialog import ConfirmDialog
from .SettingsWindow import SettingsWindow
from .LogWindow import LogWindow

# Application constants
APP_NAME = "TradingMate"
# Filepaths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_MAIN_WINDOW_FILE = os.path.join(ASSETS_DIR, "gtk", "main_window_layout.glade")
# GTK Widget IDs
MAIN_WINDOW = "main_window"
NOTEBOOK = "notebook"
OPEN_BUTTON = "open_button"
SETTINGS_BUTTON = "settings_button"
ABOUT_BUTTON = "about_button"
PORTFOLIO_PATH_LABEL = "portfolio_path_label"
SHOW_LOG_BUTTON = "show_log_button"


class UIHandler:
    def __init__(self, server):
        self._portfolio_tabs = {}
        self._client = TradingMateClient(server)
        self._data_worker = DataInterface(self._client, self._on_data_worker_timeout)
        self._create_UI()

    def _create_UI(self):
        # Load GTK layout from file
        builder = gtk.Builder()
        builder.add_from_file(GLADE_MAIN_WINDOW_FILE)
        # Get reference of each widget in the main window
        self._main_window = builder.get_object(MAIN_WINDOW)
        self._notebook = builder.get_object(NOTEBOOK)
        open_button = builder.get_object(OPEN_BUTTON)
        settings_button = builder.get_object(SETTINGS_BUTTON)
        about_button = builder.get_object(ABOUT_BUTTON)
        show_log_button = builder.get_object(SHOW_LOG_BUTTON)
        self._portfolio_path_label = builder.get_object(PORTFOLIO_PATH_LABEL)
        # and link their callbacks
        self._main_window.connect("destroy", self._on_close_main_window_event)
        open_button.connect("clicked", self._on_open_portfolio_event)
        settings_button.connect("clicked", self._on_open_settings_event)
        about_button.connect("clicked", self._on_show_about_event)
        show_log_button.connect("clicked", self._on_show_log_event)
        self._notebook.connect("switch-page", self._on_change_notebook_page)
        # Manually create required notebook pages
        for pf in self._client.get_portfolios():
            self._create_update_portfolio_tab(pf)

    def _on_close_main_window_event(self, widget):
        # Check if there are unsaved changes before closing the app
        if self._client.unsaved_changes():
            ConfirmDialog(
                self._main_window,
                Messages.UNSAVED_CHANGES.value,
                self._close_application,
            ).show()
        else:
            self._close_application()

    def _close_application(self):
        self._data_worker.shutdown()
        self._data_worker.join()
        self._client.stop()
        gtk.main_quit()

    def _on_show_about_event(self, widget):
        MessageDialog(
            self._main_window,
            "About",
            Messages.ABOUT_MESSAGE.value,
            gtk.MessageType.INFO,
        ).show()

    def _on_show_log_event(self, widget):
        LogWindow(self._main_window, self._client).show()

    def _on_data_worker_timeout(self, portfolio):
        GLib.idle_add(self._create_update_portfolio_tab, portfolio)

    def _create_update_portfolio_tab(self, portfolio):
        if portfolio.get_id() not in self._portfolio_tabs.keys():
            self._create_portfolio_tab(portfolio)
        self._portfolio_tabs[portfolio.get_id()].update_data(portfolio)

    def _create_portfolio_tab(self, portfolio):
        # Create a new PortfolioPage and add it to the notebook
        page = PortfolioPage(
            self._main_window,
            self._client,
            portfolio.get_id(),
            portfolio.get_portfolio_path(),
        )
        self._notebook.append_page(page, gtk.Label(portfolio.get_name()))
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
            MessageDialog(
                self._parent_window, "Error", str(e), gtk.MessageType.ERROR
            ).show()

    def _on_open_settings_event(self, widget):
        # FIXME changes are not applied immediately, it would be good to force a UI refresh
        SettingsWindow(self._main_window, self._client).show()

    def _on_change_notebook_page(self, widget, page_toplevel, page_index):
        self._portfolio_path_label.set_text(page_toplevel.get_portfolio_path())

    ### Public API

    def start(self):
        self._data_worker.start_delayed(2)
        self._main_window.show_all()
        gtk.main()
