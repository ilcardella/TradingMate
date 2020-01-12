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
LOG_TEXT_VIEW = "log_textview"
LOG_SCROLL_WINDOW = "log_window_scroll"
CLOSE_BUTTON = "close_button"


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
        self._log_buffer = builder.get_object(LOG_BUFFER)
        text_view = builder.get_object(LOG_TEXT_VIEW)
        self._scrolled_window = builder.get_object(LOG_SCROLL_WINDOW)
        close_button = builder.get_object(CLOSE_BUTTON)
        # Edit widgets and connect callbacks
        top_level.set_transient_for(self._parent_window)
        text_view.connect("size-allocate", self._on_text_view_changed)
        close_button.connect("clicked", self._on_close_button_event)
        return top_level

    def _on_close_button_event(self, widget):
        self._pause_tail_worker()
        self._window.hide()

    def _on_text_view_changed(self, widget, event):
        # Move the vertical adjustment of the exceeding amount
        v_adj = self._scrolled_window.get_vadjustment()
        v_adj.set_value(v_adj.get_upper() - v_adj.get_page_size())
        # Resize the window to fit the longest line plus a buffer
        h_adj = self._scrolled_window.get_hadjustment()
        self._window.resize(h_adj.get_upper(), self._window.get_size()[1])

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
        thread.start()
        return thread

    def _start_tail_worker(self):
        # If None create a new thread that tails the log file
        if self._tail_worker is None:
            self._tail_worker = self._create_tail_worker(
                self._client.get_app_log_filepath()
            )
        # Enable the worker and disable the kill event
        self._tail_worker_enabled.set()
        self._tail_worker_kill.clear()

    def _stop_tail_worker(self):
        # it's important to set the kill event before clearing the enabled one
        self._tail_worker_kill.set()
        self._tail_worker_enabled.set()
        if self._tail_worker:
            self._tail_worker.join()

    def _pause_tail_worker(self):
        self._tail_worker_enabled.clear()

    ### Public API

    def show(self):
        self._start_tail_worker()
        self._window.show_all()

    def destroy(self):
        self._stop_tail_worker()
        self._window.destroy()
