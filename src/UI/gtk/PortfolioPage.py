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
from .AddTradeWindow import AddTradeWindow
from .MessageDialog import MessageDialog

INVALID_STRING = "-"

# File paths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_NOTEBOOK_PAGE_FILE = os.path.join(ASSETS_DIR, "gtk", "notebook_page_layout.glade")

# GTK Widget IDs
NOTEBOOK_PAGE = "notebook_page_box"
SAVE_BUTTON = "save_button"
SAVE_AS_BUTTON = "save_as_button"
ADD_BUTTON = "add_button"
REFRESH_BUTTON = "refresh_button"
REFRESH_SWITCH = "auto_refresh_switch"
BALANCES_ACCOUNT_VALUE = "balances_account_value"
BALANCES_CASH_VALUE = "balances_cash_value"
BALANCES_POSITIONS_VALUE = "balances_positions_value"
BALANCES_INVESTED_VALUE = "balances_invested_cash_value"
BALANCES_PL_VALUE = "balances_pl_value"
BALANCES_PL_PC_VALUE = "balances_pl_pc_value"
TREE_POSITIONS_MODEL = "positions_tree_model"
TREE_TRADING_HISTORY_MODEL = "trading_history_tree_model"


class PortfolioPage:
    """GTK Notebook page that display information of a user portfolio"""

    def __init__(self, parent_window, portfolio_id, server):
        self._parent_window = parent_window
        self._id = portfolio_id
        self._server = server
        self._widget = self._load_UI(GLADE_NOTEBOOK_PAGE_FILE)
        self._reset_cache()

    def _load_UI(self, filepath):
        # Load GTK layour of the tab page
        builder = gtk.Builder()
        builder.add_from_file(filepath)
        # Get the buttons references
        top_level = builder.get_object(NOTEBOOK_PAGE)
        save_button = builder.get_object(SAVE_BUTTON)
        save_as_button = builder.get_object(SAVE_AS_BUTTON)
        add_button = builder.get_object(ADD_BUTTON)
        self._refresh_button = builder.get_object(REFRESH_BUTTON)
        self._refresh_switch = builder.get_object(REFRESH_SWITCH)
        # Get the labels references
        self._label_account = builder.get_object(BALANCES_ACCOUNT_VALUE)
        self._label_cash = builder.get_object(BALANCES_CASH_VALUE)
        self._label_positions = builder.get_object(BALANCES_POSITIONS_VALUE)
        self._label_invested = builder.get_object(BALANCES_INVESTED_VALUE)
        self._label_pl = builder.get_object(BALANCES_PL_VALUE)
        self._label_pl_pc = builder.get_object(BALANCES_PL_PC_VALUE)
        # Get the positions tree model reference
        self._positions_tree_model = builder.get_object(TREE_POSITIONS_MODEL)
        self._history_tree_model = builder.get_object(TREE_TRADING_HISTORY_MODEL)
        # Link callbacks to widgets
        save_button.connect("clicked", self._on_save_event)
        save_as_button.connect("clicked", self._on_save_as_event)
        add_button.connect("clicked", self._on_add_event)
        self._refresh_button.connect("clicked", self._on_refresh_event)
        self._refresh_switch.connect("state-set", self._auto_refresh_switch_set_event)
        # Set initial status of refresh switch and button based on portfolio status
        self._update_refresh_box()
        # Return the top level container
        return top_level

    def _reset_cache(self):
        self._cache = {"trade_history": []}

    def _trade_history_changed(self, trade_list):
        return False if self._cache["trade_history"] == trade_list else True

    def _on_save_event(self, widget):
        self._server.save_portfolio_event(self._id, None)

    def _on_save_as_event(self, widget):
        try:
            dialog = gtk.FileChooserDialog(
                "Select file",
                self._parent_window,
                gtk.FileChooserAction.SAVE,
                (
                    gtk.STOCK_CANCEL,
                    gtk.ResponseType.CANCEL,
                    gtk.STOCK_SAVE,
                    gtk.ResponseType.OK,
                ),
            )
            filter_json = gtk.FileFilter()
            filter_json.set_name("JSON files")
            filter_json.add_mime_type("application/json")
            dialog.add_filter(filter_json)
            dialog.set_do_overwrite_confirmation(True)
            response = dialog.run()

            if response == gtk.ResponseType.OK:
                filename = dialog.get_filename()
                if filename is not None and len(filename) > 0:
                    self._client.save_portfolio_event(self._id, filename)
            dialog.destroy()
        except RuntimeError as e:
            MessageDialog(
                self._parent_window, "Error", str(e), gtk.MessageType.ERROR
            ).show()

    def _on_add_event(self, widget):
        AddTradeWindow(self._parent_window, self._server, self._id).show()

    def _validate_value(self, value, negative_ok=False):
        if (
            value is None
            or (isinstance(value, str) and len(value) < 1)
            or (isinstance(value, float) and not negative_ok and value < 0.0)
            or (isinstance(value, int) and not negative_ok and value < 0)
        ):
            return INVALID_STRING
        if isinstance(value, float):
            value = round(value, 3)
        return str(value)

    def _update_portfolio_balances(self, portfolio):
        self._label_account.set_text(self._validate_value(portfolio.get_total_value()))
        self._label_cash.set_text(self._validate_value(portfolio.get_cash_available()))
        self._label_positions.set_text(
            self._validate_value(portfolio.get_holdings_value())
        )
        self._label_invested.set_text(
            self._validate_value(portfolio.get_cash_deposited())
        )
        self._label_pl.set_text(
            self._validate_value(portfolio.get_portfolio_pl(), negative_ok=True)
        )
        self._label_pl_pc.set_text(
            self._validate_value(portfolio.get_portfolio_pl_perc(), negative_ok=True)
        )

    def _update_positions_treeview(self, positions_list):
        self._positions_tree_model.clear()
        for h in positions_list:
            self._positions_tree_model.append(
                [
                    self._validate_value(h.get_symbol()),
                    self._validate_value(h.get_quantity()),
                    self._validate_value(h.get_open_price()),
                    self._validate_value(h.get_last_price()),
                    self._validate_value(h.get_cost()),
                    self._validate_value(h.get_value()),
                    self._validate_value(h.get_profit_loss(), negative_ok=True),
                    self._validate_value(h.get_profit_loss_perc(), negative_ok=True),
                ]
            )

    def _update_trading_history_treeview(self, trade_list):
        if self._trade_history_changed(trade_list):
            self._cache["trade_history"] = trade_list
            self._history_tree_model.clear()
            for t in trade_list:
                self._history_tree_model.append(
                    [
                        self._validate_value(t.date.strftime("%d/%m/%Y")),
                        self._validate_value(t.action.name),
                        self._validate_value(t.symbol),
                        self._validate_value(t.quantity),
                        self._validate_value(t.price),
                        self._validate_value(t.fee),
                        self._validate_value(t.sdr),
                        self._validate_value(t.total, negative_ok=True),
                    ]
                )

    def _on_refresh_event(self, widget):
        # Temporary disable the refresh button
        self._refresh_button.set_sensitive(False)
        self._server.manual_refresh_event(self._id)

    def _auto_refresh_switch_set_event(self, widget, switch_is_on):
        self._server.set_auto_refresh_event(switch_is_on, self._id)
        self._update_refresh_box()

    def _update_refresh_box(self):
        if self._server.is_portfolio_auto_refreshing(self._id):
            self._refresh_switch.set_active(True)
            self._refresh_button.set_sensitive(False)
        else:
            self._refresh_switch.set_active(False)
            self._refresh_button.set_sensitive(True)

    ### Public API

    def get_top_level(self):
        return self._widget

    def update_data(self, portfolio):
        # Update account balances labels
        self._update_portfolio_balances(portfolio)
        # Update current positions tree
        self._update_positions_treeview(portfolio.get_holding_list())
        # Update history tree
        self._update_trading_history_treeview(portfolio.get_trade_history()[::-1])
        # Restore refresh box status
        self._update_refresh_box()
