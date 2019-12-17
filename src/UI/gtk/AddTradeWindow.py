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

# File paths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_ADD_TRADE_WINDOW_FILE = os.path.join(ASSETS_DIR, "add_trade_window_layout.glade")

# GTK Widget IDs
ADD_TRADE_WINDOW = "add_trade_window"


class AddTradeWindow:
    def __init__(self, server):
        self._server = server
        self._window = self._load_UI(GLADE_ADD_TRADE_WINDOW_FILE)

    def _load_UI(self, filepath):
        builder = gtk.Builder()
        builder.add_from_file(filepath)
        # TODO get widget references and link callbacks

    ### Public API

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.destroy()
