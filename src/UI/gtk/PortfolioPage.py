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

INVALID_STRING = "-"

# File paths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_NOTEBOOK_PAGE_FILE = os.path.join(ASSETS_DIR, "notebook_page_layout.glade")

# GTK Widget IDs
NOTEBOOK_PAGE = "notebook_page_box"
SAVE_BUTTON = "save_button"
SAVE_AS_BUTTON = "save_as_button"
ADD_BUTTON = "add_button"
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

    def __init__(self, portfolio_id, server):
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
        # TODO add manual refresh button and auto refresh toggle
        # Get the labels references
        self.label_account = builder.get_object(BALANCES_ACCOUNT_VALUE)
        self.label_cash = builder.get_object(BALANCES_CASH_VALUE)
        self.label_positions = builder.get_object(BALANCES_POSITIONS_VALUE)
        self.label_invested = builder.get_object(BALANCES_INVESTED_VALUE)
        self.label_pl = builder.get_object(BALANCES_PL_VALUE)
        self.label_pl_pc = builder.get_object(BALANCES_PL_PC_VALUE)
        # Get the positions tree model reference
        self.positions_tree_model = builder.get_object(TREE_POSITIONS_MODEL)
        self.history_tree_model = builder.get_object(TREE_TRADING_HISTORY_MODEL)
        # Link callbacks to widgets
        save_button.connect("clicked", self._on_save_event)
        save_as_button.connect("clicked", self._on_save_as_event)
        add_button.connect("clicked", self._on_add_event)
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
            print(f"save as portfolio {self._id}")
            # TODO use GTK file selector
            # filename = filedialog.asksaveasfilename(
            #     initialdir=Utils.get_install_path(),
            #     title="Select file",
            #     filetypes=(("json files", "*.json"), ("all files", "*.*")),
            # )
            # if filename is not None and len(filename) > 0:
            #     self._client.save_portfolio_event(portfolio_id, filename)
        except RuntimeError as e:
            # TODO Use GTK warning window
            # WarningWindow(self.parent, "Warning", e)
            print("save as exception")

    def _on_add_event(self, widget):
        print("add event")
        # TODO show the GTK add trade window which would handle the server call by itself
        # AddTradeWindow(self._server).show()

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
        self.label_account.set_text(self._validate_value(portfolio.get_total_value()))
        self.label_cash.set_text(self._validate_value(portfolio.get_cash_available()))
        self.label_positions.set_text(
            self._validate_value(portfolio.get_holdings_value())
        )
        self.label_invested.set_text(
            self._validate_value(portfolio.get_cash_deposited())
        )
        self.label_pl.set_text(
            self._validate_value(portfolio.get_portfolio_pl(), negative_ok=True)
        )
        self.label_pl_pc.set_text(
            self._validate_value(portfolio.get_portfolio_pl_perc(), negative_ok=True)
        )

    def _update_positions_treeview(self, positions_list):
        self.positions_tree_model.clear()
        for h in positions_list:
            self.positions_tree_model.append(
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
            self.history_tree_model.clear()
            for t in trade_list:
                self.history_tree_model.append(
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
