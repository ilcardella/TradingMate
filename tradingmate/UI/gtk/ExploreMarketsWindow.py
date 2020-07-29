import inspect
import os
import sys
from datetime import datetime as dt

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils

from .MessageDialog import MessageDialog

# File paths
ASSETS_DIR = os.path.join(Utils.get_install_path(), "data", "assets")
GLADE_EXPLORE_MARKETS_WINDOW_FILE = os.path.join(
    ASSETS_DIR, "gtk", "explore_markets_window_layout.glade"
)

# GTK Widget IDs
EXPLORE_MARKETS_WINDOW = "explore_markets_window"
SEARCH_ENTRY = "search_entry"
MARKET_INFO_MODEL = "market_info_treeview_model"
DIVIDENDS_MODEL = "dividends_treeview_model"


class ExploreMarketsWindow:
    def __init__(self, parent_window, client):
        self._parent_window = parent_window
        self._client = client
        self._window = self._load_UI(GLADE_EXPLORE_MARKETS_WINDOW_FILE)

    def _load_UI(self, filepath):
        builder = gtk.Builder()
        builder.add_from_file(filepath)
        # Get widget references
        top_level = builder.get_object(EXPLORE_MARKETS_WINDOW)
        top_level.set_transient_for(self._parent_window)
        # Search entry
        self.search = builder.get_object(SEARCH_ENTRY)
        self.search.connect("activate", self._on_search_enter_event)
        # Market info tree view
        self.market_info_model = builder.get_object(MARKET_INFO_MODEL)
        # Dividends tree view
        self.dividends_model = builder.get_object(DIVIDENDS_MODEL)
        # Return the main container
        return top_level

    def _validate_value(self, value, negative_ok=False):
        if (
            value is None
            or (isinstance(value, str) and len(value) < 1)
            or (isinstance(value, float) and not negative_ok and value < 0.0)
            or (isinstance(value, int) and not negative_ok and value < 0)
        ):
            return "-"
        if isinstance(value, float):
            value = round(value, 3)
        return str(value)

    def _validate_date(self, date):
        try:
            return dt.strftime(date, "%d/%m/%Y")
        except:
            return "-"

    def _clear_content(self):
        self.market_info_model.clear()
        self.dividends_model.clear()

    def _on_search_enter_event(self, widget):
        try:
            ticker = self.search.get_text()
            data = self._client.get_market_details(ticker)
            self._update_UI(data)
        except Exception as e:
            MessageDialog(
                self._parent_window, "Error", str(e), gtk.MessageType.ERROR
            ).show()

    def _update_UI(self, data):
        self._update_market_info(data["info"])
        self._update_dividends(data["dividends"])
        self._update_financials(data["financials"])
        self._update_balance_sheet(data["balance_sheet"])
        self._update_cashflow(data["cashflow"])
        self._update_earnings(data["earnings"])

    def _update_market_info(self, info):
        self.market_info_model.clear()
        self.market_info_model.append(["Name", self._validate_value(info["longName"])])
        self.market_info_model.append(["Symbol", self._validate_value(info["symbol"])])
        self.market_info_model.append(["Market", self._validate_value(info["market"])])
        self.market_info_model.append(
            ["Country", self._validate_value(info["country"])]
        )
        self.market_info_model.append(
            ["Currency", self._validate_value(info["currency"])]
        )
        self.market_info_model.append(["Sector", self._validate_value(info["sector"])])
        self.market_info_model.append(
            ["Industry", self._validate_value(info["industry"])]
        )
        self.market_info_model.append(
            ["Website", self._validate_value(info["website"])]
        )
        date = (
            dt.fromtimestamp(info["exDividendDate"])
            if "exDividendDate" in info and info["exDividendDate"] is not None
            else "-"
        )
        self.market_info_model.append(["Ex date", self._validate_date(date)])
        market_cap = (
            info["marketCap"] / 1000000 if isinstance(info["marketCap"], int) else "-"
        )
        self.market_info_model.append(
            ["Market cap [M]", self._validate_value(market_cap)]
        )
        self.market_info_model.append(["Ask", self._validate_value(info["ask"])])
        self.market_info_model.append(["Bid", self._validate_value(info["bid"])])
        self.market_info_model.append(
            ["Shares", self._validate_value(info["sharesOutstanding"])]
        )

    def _update_dividends(self, dividends):
        self.dividends_model.clear()
        for date, value in dividends[::-1].iteritems():
            self.dividends_model.append(
                [self._validate_date(date.to_pydatetime()), self._validate_value(value)]
            )

    def _update_financials(self, financials):
        # TODO
        pass

    def _update_balance_sheet(self, balances):
        # TODO
        pass

    def _update_cashflow(self, cashflow):
        # TODO
        pass

    def _update_earnings(self, earnings):
        # TODO
        pass

    ### Public API

    def show(self):
        self._clear_content()
        self._window.show_all()

    def destroy(self):
        # Do not destroy so that the window is kept in memory for re-use
        self._window.hide()
