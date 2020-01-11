import os
import sys
import inspect
import threading
from pygtail import Pygtail
import time
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk, GLib

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
        self._tail_worker_enabled = threading.Event()
        self._tail_worker_kill = threading.Event()

    def _load_UI(self, filepath):
        # Load GTK layout from glade file
        builder = gtk.Builder()
        builder.add_from_file(filepath)
        top_level = builder.get_object(LOG_WINDOW)
        top_level.set_transient_for(self._parent_window)
        top_level.connect("destroy", self._on_window_destroy)
        self._log_buffer = builder.get_object(LOG_BUFFER)
        return top_level

    def _on_window_destroy(self, widget):
        self._stop_tail_worker()

    def _tail_lines(self, filepath):
        tail = Pygtail(filepath)
        while True:
            try:
                self._tail_worker_enabled.wait()
                if self._tail_worker_kill.is_set():
                    return
                line = tail.next()
                GLib.idle_add(self._add_line_to_log_buffer, line)
            except StopIteration:
                time.sleep(0.5)

    def _add_line_to_log_buffer(self, line):
        it = self._log_buffer.get_end_iter()
        self._log_buffer.insert(it, line, len(line))
        self._log_buffer.insert(it, "\n")

    def _create_tail_worker(self, filepath):
        # Create a daemon thread that tails the log file
        thread = threading.Thread(target=self._tail_lines, args=(filepath,))
        thread.setDaemon(True)
        return thread

    def _start_tail_worker(self):
        # Start a new thread that tails the log file
        if self._tail_worker is None:
            self._tail_worker = self._create_tail_worker(
                self._client.get_app_log_filepath()
            )
            self._tail_worker.start()
        self._tail_worker_enabled.set()
        self._tail_worker_kill.clear()

    def _stop_tail_worker(self):
        # it's important to set the kill event before clearing the enabled one
        self._tail_worker_kill.set()
        self._tail_worker_enabled.set()
        self._tail_worker.join()

    ### Public API

    def show(self):
        self._log_buffer.set_text("")  # clear content
        self._start_tail_worker()
        self._window.show_all()

    def destroy(self):
        self._tail_worker_enabled.clear()
        # Do not destroy so that the window is kept in memory for re-use
        self._window.hide()
