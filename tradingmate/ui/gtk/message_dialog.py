# flake8: noqa: E402 # Required to allow use of gi.require_version

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk


class MessageDialog:
    def __init__(self, parent_window, title, message, dialog_type):
        """
        Valid "dialog_type":
         - gtk.MessageType.INFO
         - gtk.MessageType.ERROR
         - gtk.MessageType.WARNING
         - gtk.MessageType.QUESTION
        """
        self._dialog = gtk.MessageDialog(
            parent_window, 0, dialog_type, gtk.ButtonsType.OK, str(title)
        )
        self._dialog.format_secondary_text(str(message))
        self._dialog.set_modal(True)

    def show(self):
        self._dialog.run()
        self._dialog.destroy()
