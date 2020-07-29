import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib
from gi.repository import Gtk as gtk

from tradingmate.UI.DataInterface import DataInterface
from tradingmate.UI.gtk.ConfirmDialog import ConfirmDialog
from tradingmate.UI.gtk.ExploreMarketsWindow import ExploreMarketsWindow
from tradingmate.UI.gtk.LogWindow import LogWindow
from tradingmate.UI.gtk.MessageDialog import MessageDialog
from tradingmate.UI.gtk.PortfolioPage import PortfolioPage
from tradingmate.UI.gtk.SettingsWindow import SettingsWindow
from tradingmate.UI.TradingMateClient import TradingMateClient
from tradingmate.Utils.Utils import Messages, Utils

# Application constants
APP_NAME = "TradingMate"
# Filepaths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_MAIN_WINDOW_FILE = os.path.join(ASSETS_DIR, "gtk", "main_window_layout.glade")
# GTK Widget IDs
MAIN_WINDOW = "main_window"
NOTEBOOK = "notebook"
OPEN_BUTTON = "header_open_button"
SETTINGS_BUTTON = "main_header_settings_button"
ABOUT_BUTTON = "main_header_about_button"
PORTFOLIO_PATH_LABEL = "portfolio_path_label"
SHOW_LOG_BUTTON = "main_header_log_button"
CONNECTION_IMAGE = "connection_image"
PROPERTIES_BUTTON = "properties_button"
PROPERTIES_POPOVER = "main_header_properties_popover"
EXPLORE_BUTTON = "header_explore_button"


class UIHandler:
    def __init__(self, server):
        self._portfolio_tabs = {}
        self._client = TradingMateClient(server)
        self._data_worker = DataInterface(self._client, self._on_data_worker_timeout)
        self._create_UI()
        self._log_window = LogWindow(self._main_window, self._client)

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
        self._connection_status_image = builder.get_object(CONNECTION_IMAGE)
        properties_button = builder.get_object(PROPERTIES_BUTTON)
        self._properties_popover = builder.get_object(PROPERTIES_POPOVER)
        explore_button = builder.get_object(EXPLORE_BUTTON)
        # configure widgets
        self._properties_popover.set_relative_to(properties_button)
        # and link their callbacks
        self._main_window.connect("delete-event", self._on_main_window_delete_event)
        properties_button.connect("clicked", self._on_properties_button_click_event)
        open_button.connect("clicked", self._on_open_portfolio_event)
        settings_button.connect("clicked", self._on_open_settings_event)
        about_button.connect("clicked", self._on_show_about_event)
        show_log_button.connect("clicked", self._on_show_log_event)
        self._notebook.connect("switch-page", self._on_change_notebook_page)
        explore_button.connect("clicked", self._on_explore_button_clicked)
        # Manually create required notebook pages
        for pf in self._client.get_portfolios():
            self._create_update_portfolio_tab(pf)

    def _on_main_window_delete_event(self, *args):
        # Check if there are unsaved changes before closing the app
        if self._client.unsaved_changes():
            ConfirmDialog(
                self._main_window,
                Messages.UNSAVED_CHANGES.value,
                self._close_application,
            ).show()
        else:
            self._close_application()
            return False
        # Return True to block event propagation
        return True

    def _close_application(self):
        if self._log_window:
            self._log_window.destroy()
        self._data_worker.shutdown()
        self._data_worker.join()
        self._client.stop()
        gtk.main_quit()

    def _on_properties_button_click_event(self, widget):
        self._properties_popover.show_all()
        self._properties_popover.popup()

    def _on_show_about_event(self, widget):
        # Hide the popover menu and shows the about dialog
        self._properties_popover.hide()
        message = "Version: {}\n{}".format(
            self._client.get_app_version(), Messages.ABOUT_MESSAGE.value
        )
        MessageDialog(self._main_window, "About", message, gtk.MessageType.INFO).show()

    def _on_show_log_event(self, widget):
        # Hide the popover menu and shows the log window
        self._properties_popover.hide()
        self._log_window.show()

    def _on_data_worker_timeout(self, portfolios):
        # Update the connection status image based on portfolio data
        offline_portfolios = len([p for p in portfolios if p.get_total_value() is None])
        GLib.idle_add(
            self._update_connection_status, False if offline_portfolios else True
        )
        for pf in portfolios:
            GLib.idle_add(self._create_update_portfolio_tab, pf)

    def _update_connection_status(self, connected):
        self._connection_status_image.set_from_icon_name(
            "gtk-connect" if connected else "gtk-disconnect", gtk.IconSize.BUTTON
        )
        self._connection_status_image.set_tooltip_text(
            "Online" if connected else "Offline"
        )

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
                self._main_window, "Error", str(e), gtk.MessageType.ERROR
            ).show()

    def _on_open_settings_event(self, widget):
        # Hide the popover menu and shows the settings window
        self._properties_popover.hide()
        # FIXME changes are not applied immediately, it would be good to force a UI refresh
        SettingsWindow(self._main_window, self._client).show()

    def _on_change_notebook_page(self, widget, page_toplevel, page_index):
        self._portfolio_path_label.set_text(page_toplevel.get_portfolio_path())

    def _on_explore_button_clicked(self, widget):
        ExploreMarketsWindow(self._main_window, self._client).show()

    ### Public API

    def start(self):
        self._data_worker.start_delayed(2)
        self._main_window.show_all()
        gtk.main()
