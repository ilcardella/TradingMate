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

    def __init__(self, parent, server):
        self._parent = parent
        self._server = server
        self.data_interface = DataInterface(server, self._on_portfolio_update)

    def _on_portfolio_update(self, portfolio):
        """Handle new incoming portfolio update"""
        # Call the parent view to update the portfolio tab
        self._parent.update_portfolio_tab(portfolio)

    def start(self):
        """Handle start event"""
        self.data_interface.start()

    def stop(self):
        """Handle stop event"""
        self.data_interface.shutdown()
        self.data_interface.join()
        self._server.close_view_event()

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
