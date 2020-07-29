import datetime
import os

import gi

gi.require_version("Gtk", "3.0")  # noqa
from gi.repository import Gtk as gtk  # noqa

from tradingmate.ui.gtk.MessageDialog import MessageDialog
from tradingmate.utils.Trade import DATETIME_FORMAT, TIME_FORMAT, Trade
from tradingmate.utils.Utils import Actions, Markets, Messages, Utils

# File paths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_ADD_TRADE_WINDOW_FILE = os.path.join(
    ASSETS_DIR, "gtk", "add_trade_window_layout.glade"
)

# GTK Widget IDs
ADD_TRADE_WINDOW = "add_trade_window"
DATE_CALENDAR = "date_calendar"
TIME_ENTRY = "time_entry"
ACTION_COMBO = "action_combo"
MARKET_COMBO = "market_combo"
SYMBOL_ENTRY = "symbol_entry"
QUANTITY_ENTRY = "quantity_entry"
PRICE_ENTRY = "price_entry"
FEE_ENTRY = "fee_entry"
SDR_ENTRY = "sdr_entry"
NOTES_ENTRY = "notes_entry"
CANCEL_BUTTON = "cancel_button"
ADD_BUTTON = "add_button"


class AddTradeWindow:
    def __init__(self, parent_window, client, portfolio_id):
        self._parent_window = parent_window
        self._client = client
        self._portfolio_id = portfolio_id
        self._window = self._load_UI(GLADE_ADD_TRADE_WINDOW_FILE)

    def _load_UI(self, filepath):
        builder = gtk.Builder()
        builder.add_from_file(filepath)
        # Get widget references
        top_level = builder.get_object(ADD_TRADE_WINDOW)
        top_level.set_transient_for(self._parent_window)
        top_level.set_modal(True)
        self._calendar = builder.get_object(DATE_CALENDAR)
        self._time_entry = builder.get_object(TIME_ENTRY)
        self._action_combo = builder.get_object(ACTION_COMBO)
        self._market_combo = builder.get_object(MARKET_COMBO)
        self._symbol_entry = builder.get_object(SYMBOL_ENTRY)
        self._quantity_entry = builder.get_object(QUANTITY_ENTRY)
        self._price_entry = builder.get_object(PRICE_ENTRY)
        self._fee_entry = builder.get_object(FEE_ENTRY)
        self._sdr_entry = builder.get_object(SDR_ENTRY)
        self._notes_entry = builder.get_object(NOTES_ENTRY)
        self._cancel_button = builder.get_object(CANCEL_BUTTON)
        self._add_button = builder.get_object(ADD_BUTTON)
        # Register callbacks
        self._calendar.connect("day-selected", self._on_date_selected)
        self._time_entry.connect("changed", self._on_entry_changed)
        self._symbol_entry.connect("changed", self._on_entry_changed)
        self._quantity_entry.connect("changed", self._on_entry_changed)
        self._price_entry.connect("changed", self._on_entry_changed)
        self._fee_entry.connect("changed", self._on_entry_changed)
        self._sdr_entry.connect("changed", self._on_entry_changed)
        self._notes_entry.connect("changed", self._on_entry_changed)
        self._action_combo.connect("changed", self._on_action_change_event)
        self._cancel_button.connect("clicked", self._on_cancel_event)
        self._add_button.connect("clicked", self._on_add_event)
        # Load widgets with static content
        self._load_static_content()
        return top_level

    def _on_cancel_event(self, widget):
        self.destroy()

    def _on_add_event(self, widget):
        # Normalise widgets content with default values if necessary
        year, month, day = self._calendar.get_date()
        date_string = f"{day}/{month+1}/{year}"
        time_string = self._time_entry.get_text()
        date = datetime.datetime.strptime(
            "{} {}".format(date_string, time_string), DATETIME_FORMAT
        )
        action = Actions[self._action_combo.get_active_text()]
        quantity = float(
            self._quantity_entry.get_text()
            if len(self._quantity_entry.get_text()) > 0
            else 0
        )
        market = (
            f"{Markets[self._market_combo.get_active_text()].name}:{self._symbol_entry.get_text()}"
            if self._market_combo.get_active_text()
            else ""
        )
        price = float(
            self._price_entry.get_text() if len(self._price_entry.get_text()) else 0
        )
        fee = float(
            self._fee_entry.get_text() if len(self._fee_entry.get_text()) else 0
        )
        sdr = float(
            self._sdr_entry.get_text() if len(self._sdr_entry.get_text()) else 0
        )
        notes = str(self._notes_entry.get_text())
        # Create a Trade instance from the widgets content
        t = Trade(date, action, quantity, market, price, fee, sdr, notes)
        # Call server and handle errors
        try:
            self._client.new_trade_event(t, self._portfolio_id)
            self.destroy()
        except RuntimeError as e:
            MessageDialog(
                self._parent_window, "Error", str(e), gtk.MessageType.ERROR
            ).show()

    def _on_action_change_event(self, widget):
        # Clear widget content
        self._clear_content(clear_calendar=False)
        # Enable/disable widgets
        action = Actions[self._action_combo.get_active_text()]
        if action == Actions.BUY:
            self._market_combo.set_sensitive(True)
            self._symbol_entry.set_sensitive(True)
            self._quantity_entry.set_sensitive(True)
            self._price_entry.set_sensitive(True)
            self._fee_entry.set_sensitive(True)
            self._sdr_entry.set_sensitive(True)
            self._notes_entry.set_sensitive(True)
        elif action == Actions.SELL:
            self._market_combo.set_sensitive(True)
            self._symbol_entry.set_sensitive(True)
            self._quantity_entry.set_sensitive(True)
            self._price_entry.set_sensitive(True)
            self._fee_entry.set_sensitive(True)
            self._sdr_entry.set_sensitive(False)
            self._notes_entry.set_sensitive(True)
        elif action == Actions.DEPOSIT:
            self._market_combo.set_sensitive(False)
            self._symbol_entry.set_sensitive(False)
            self._quantity_entry.set_sensitive(True)
            self._price_entry.set_sensitive(False)
            self._fee_entry.set_sensitive(False)
            self._sdr_entry.set_sensitive(False)
            self._notes_entry.set_sensitive(True)
        elif action == Actions.DIVIDEND:
            self._market_combo.set_sensitive(True)
            self._symbol_entry.set_sensitive(True)
            self._quantity_entry.set_sensitive(True)
            self._price_entry.set_sensitive(False)
            self._fee_entry.set_sensitive(False)
            self._sdr_entry.set_sensitive(False)
            self._notes_entry.set_sensitive(True)
        elif action == Actions.WITHDRAW:
            self._market_combo.set_sensitive(False)
            self._symbol_entry.set_sensitive(False)
            self._quantity_entry.set_sensitive(True)
            self._price_entry.set_sensitive(False)
            self._fee_entry.set_sensitive(False)
            self._sdr_entry.set_sensitive(False)
            self._notes_entry.set_sensitive(True)
        elif action == Actions.FEE:
            self._market_combo.set_sensitive(False)
            self._symbol_entry.set_sensitive(False)
            self._quantity_entry.set_sensitive(True)
            self._price_entry.set_sensitive(False)
            self._fee_entry.set_sensitive(False)
            self._sdr_entry.set_sensitive(False)
            self._notes_entry.set_sensitive(True)
        else:
            self._market_combo.set_sensitive(True)
            self._symbol_entry.set_sensitive(True)
            self._quantity_entry.set_sensitive(True)
            self._price_entry.set_sensitive(True)
            self._fee_entry.set_sensitive(True)
            self._sdr_entry.set_sensitive(True)
            self._notes_entry.set_sensitive(True)
            MessageDialog(
                self._parent_window,
                "Warning",
                Messages.WINDOW_UNSUPPORTED_ACTION.value,
                gtk.MessageType.WARNING,
            ).show()

    def _on_date_selected(self, widget):
        self._check_data_validity()

    def _on_entry_changed(self, widget):
        if widget is self._symbol_entry:
            self._symbol_entry.set_text(self._symbol_entry.get_text().upper())
        self._check_data_validity()

    def _load_static_content(self):
        # Calendar
        now = datetime.datetime.now()
        self._calendar.select_month(now.month - 1, now.year)
        self._calendar.select_day(0)  # Clear day selection
        # Time
        self._time_entry.set_text("00:00")
        # Combo action
        self._action_combo.remove_all()
        for a in Actions:
            self._action_combo.append_text(a.name)
        # Combo market
        self._market_combo.remove_all()
        for m in Markets:
            self._market_combo.append_text(m.name)

    def _clear_content(self, clear_calendar=True):
        # Clear day selection in calendar and time
        if clear_calendar:
            self._calendar.select_day(0)
            self._time_entry.set_text("00:00")
        # Reset entries
        self._symbol_entry.set_text("")
        self._quantity_entry.set_text("")
        self._price_entry.set_text("")
        self._fee_entry.set_text("")
        self._sdr_entry.set_text("")
        self._notes_entry.set_text("")

    def _check_data_validity(self):
        year, month, date = self._calendar.get_date()
        valid = all(
            [
                0 < date < 32,
                self._is_time_valid(self._time_entry.get_text()),
                not self._symbol_entry.get_sensitive()
                or self._is_string_valid(self._symbol_entry.get_text()),
                not self._quantity_entry.get_sensitive()
                or self._is_float_valid(self._quantity_entry.get_text()),
                not self._price_entry.get_sensitive()
                or self._is_float_valid(self._price_entry.get_text()),
                not self._fee_entry.get_sensitive()
                or self._is_float_valid(self._fee_entry.get_text(), zero_ok=True),
                not self._sdr_entry.get_sensitive()
                or self._is_float_valid(self._sdr_entry.get_text(), zero_ok=True),
                not self._notes_entry.get_sensitive()
                or self._is_string_valid(self._notes_entry.get_text(), empty_ok=True),
            ]
        )
        self._add_button.set_sensitive(valid)

    def _is_string_valid(self, string_value, empty_ok=False):
        try:
            s = str(string_value)
            return False if len(s) < 1 and not empty_ok else True
        except:
            return False

    def _is_float_valid(self, string_value, zero_ok=False):
        try:
            f = float(string_value)
            if f > 0.0 or (f == 0.0 and zero_ok):
                return True
            return False
        except:
            return False

    def _is_time_valid(self, string):
        try:
            date = datetime.datetime.strptime(string, TIME_FORMAT)
            return True
        except:
            return False

    ### Public API

    def show(self):
        self._clear_content()
        self._window.show_all()

    def destroy(self):
        # Do not destroy so that the window is kept in memory for re-use
        self._window.hide()
