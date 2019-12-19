import os
import sys
import inspect
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils, Messages
from .MessageDialog import MessageDialog

# File paths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_SETTINGS_WINDOW_FILE = os.path.join(ASSETS_DIR, "settings_window_layout.glade")

# GTK Widget IDs
SETTINGS_WINDOW = "settings_window"
PORTFOLIO_PATH_BUFFER = "portfolio_path_text_buffer"
CREDENTIALS_PATH_ENTRY = "credentials_path_entry"
CANCEL_BUTTON = "cancel_button"
SAVE_BUTTON = "save_button"


class SettingsWindow:
    def __init__(self, parent_window, client):
        self._parent_window = parent_window
        self._client = client
        self._window = self._load_UI(GLADE_SETTINGS_WINDOW_FILE)

    def _load_UI(self, filepath):
        builder = gtk.Builder()
        builder.add_from_file(filepath)
        # Get widget references and link callbacks
        top_level = builder.get_object(SETTINGS_WINDOW)
        top_level.set_transient_for(self._parent_window)
        top_level.set_modal(True)
        self._portfolio_path_buffer = builder.get_object(PORTFOLIO_PATH_BUFFER)
        self._credentials_path_entry = builder.get_object(CREDENTIALS_PATH_ENTRY)
        self._cancel_button = builder.get_object(CANCEL_BUTTON)
        self._save_button = builder.get_object(SAVE_BUTTON)
        self._cancel_button.connect("clicked", self._on_cancel_event)
        self._save_button.connect("clicked", self._on_save_event)
        # Return main container
        return top_level

    def _on_cancel_event(self, widget):
        self.destroy()

    def _on_save_event(self, widget):
        # Get config structure
        config = self._client.get_settings_event()
        # Update trading log paths from the multiline text editor
        start = self._portfolio_path_buffer.get_start_iter()
        end = self._portfolio_path_buffer.get_end_iter()
        config["trading_logs"] = self._portfolio_path_buffer.get_text(
            start, end, True
        ).split()
        # Update the credentials file path
        config["general"][
            "credentials_filepath"
        ] = self._credentials_path_entry.get_text()
        try:
            self._client.save_settings_event(config)
        except Exception as e:
            MessageDialog(
                self._window,
                "Error",
                f"{Messages.ERROR_SAVE_SETTINGS.value}: {e}",
                gtk.MessageType.ERROR,
            )
        self.destroy()

    ### Public API

    def show(self):
        config = self._client.get_settings_event()
        self._portfolio_path_buffer.set_text("")  # clear content
        it = self._portfolio_path_buffer.get_start_iter()
        for path in config["trading_logs"]:
            self._portfolio_path_buffer.insert(it, path, len(path))
            self._portfolio_path_buffer.insert(it, "\n")
        self._credentials_path_entry.set_text(config["general"]["credentials_filepath"])
        self._window.show_all()

    def destroy(self):
        # Instead of destroy use hide to keep the window in memory for re-use
        self._window.hide()
