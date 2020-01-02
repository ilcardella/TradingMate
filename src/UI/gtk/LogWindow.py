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
GLADE_FILE = os.path.join(ASSETS_DIR, "gtk", "log_window_layout.glade")

# GTK widgets ids
LOG_WINDOW = "log_window"
LOG_BUFFER = "log_buffer"


class LogWindow:
    def __init__(self, parent_window, client):
        self._parent_window = parent_window
        self._client = client
        self._window = self._load_UI(GLADE_FILE)
        self._tail_worker = None

    def _load_UI(self, filepath):
        # Load GTK layout from glade file
        builder = gtk.Builder()
        builder.add_from_file(filepath)
        top_level = builder.get_object(LOG_WINDOW)
        top_level.set_transient_for(self._parent_window)
        self._log_buffer = builder.get_object(LOG_BUFFER)
        return top_level

    # def tail_lines(self, filepath):
    #     self._log_buffer.set_text("")  # clear content
    #     it = self._log_buffer.get_start_iter()
    #     for line in Pygtail(filepath):
    #         self._log_buffer.insert(it, line, len(line))
    #         self._log_buffer.insert(it, "\n")

    def _start_tail_worker(self):
        filepath = self._client.get_app_log_filepath()
        print(f'tailing {filepath}')
        # TODO start thread to tail log file

    ### Public API

    def show(self):
        self._start_tail_worker()
        self._window.show_all()

    def destroy(self):
        # TODO stop thread to tail log file
        # Do not destroy so that the window is kept in memory for re-use
        self._window.hide()
