import os
import sys
import inspect
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


class ConfirmDialog:
    def __init__(self, parent_window, message, ok_callback=None, cancel_callback=None):
        self._ok_callback = ok_callback
        self._cancel_callback = cancel_callback

        self._dialog = gtk.Dialog(
            "Message",
            parent_window,
            0,
            (
                gtk.STOCK_CANCEL,
                gtk.ResponseType.CANCEL,
                gtk.STOCK_OK,
                gtk.ResponseType.OK,
            ),
        )
        self._dialog.set_modal(True)
        self._dialog.get_content_area().add(gtk.Label(message))
        self._dialog.show_all()

    def show(self):
        response = self._dialog.run()
        if response == gtk.ResponseType.OK and self._ok_callback is not None:
            self._ok_callback()
        elif response == gtk.ResponseType.CANCEL and self._cancel_callback is not None:
            self._cancel_callback()
        self._dialog.destroy()
