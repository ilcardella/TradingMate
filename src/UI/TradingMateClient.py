import os
import sys
import inspect
import logging

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from .DataInterface import DataInterface


class TradingMateClient:
    """Client interface to the TradingMate business logic"""

    def __init__(self, server):
        self._server = server

    def stop(self):
        """Handle stop event"""
        self._server.close_view_event()

    def get_portfolios(self):
        """Get the loaded portfolios"""
        return self._server.get_portfolios()

    def new_trade_event(self, new_trade, portfolio_id):
        """Push new trade notification to the server"""
        self._server.new_trade_event(new_trade, portfolio_id)

    def delete_last_trade_event(self, portfolio_id):
        """Request last trade deletion to the server"""
        self._server.delete_last_trade_event(portfolio_id)

    def manual_refresh_event(self, portfolio_id):
        """Request server to refresh portfolio data"""
        self._server.manual_refresh_event(portfolio_id)

    def set_auto_refresh_event(self, value, portfolio_id):
        """Set server to automatically update data for the portfolio"""
        self._server.set_auto_refresh(value, portfolio_id)

    def open_portfolio_event(self, filepath):
        """Request server to open a portfolio"""
        self._server.open_portfolio_event(filepath)

    def save_portfolio_event(self, portfolio_id, filepath):
        """Request server to save a portfolio"""
        self._server.save_portfolio_event(portfolio_id, filepath)

    def get_settings_event(self):
        """Request server to fetch TradingMate settings"""
        return self._server.get_settings_event()

    def save_settings_event(self, settings):
        """Request server to save the settings"""
        self._server.save_settings_event(settings)

    def unsaved_changes(self):
        """Request if open portfolios have unsaved changes and return True"""
        for pf in self._server.get_portfolios():
            if pf.has_unsaved_changes():
                return True
        return False

    def is_portfolio_auto_refreshing(self, portfolio_id):
        """Return True if portfolio has data auto refresh enabled, False otherwise"""
        pf = list(
            filter(lambda p: p.get_id() == portfolio_id, self._server.get_portfolios())
        )
        if pf is not None and len(pf) == 1:
            return pf[0].get_auto_refresh_enabled()
        else:
            raise ValueError(f"Portfolio {portfolio_id} does not exists")
