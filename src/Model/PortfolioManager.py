import os
import sys
import inspect
import json
import logging

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.ConfigurationManager import ConfigurationManager
from Utils.TaskThread import TaskThread
from Utils.Utils import Messages, Actions, Callbacks, Utils
from .Portfolio import Portfolio
from .StockPriceGetter import StockPriceGetter
from .DatabaseHandler import DatabaseHandler


class PortfolioManager():

    def __init__(self, config):
        self._read_configuration(config)
        # DataStruct containing the callbacks
        self.callbacks = {}
        # Database handler
        self.db_handler = DatabaseHandler(config)
        # Portfolio instance
        self.portfolio = Portfolio("Portfolio1", config)

# INTERNAL FUNCTIONS

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def _read_configuration(self, config):
        pass

    def _reset(self, filepath=None):
        self._read_configuration()
        self.db_handler.read_data(filepath)
        self.portfolio.reload()

# GETTERS

    def get_log_as_list(self):
        return self.portfolio.trading_history['trades']

    def get_portfolio(self):
        """
        Return the portfolio as instance of Portfolio class
        """
        return self.portfolio

    def get_db_filepath(self):
        return self.db_handler.get_db_filepath()

# INTERFACES

    def start(self):
        self.log = self.db_handler.read_data()
        self.portfolio.reload()
        self.livePricesThread.set_symbol_list(
            self.portfolio.get_holding_symbols())
        self.livePricesThread.start()

    def stop_application(self):
        self.livePricesThread.shutdown()
        self.livePricesThread.join()
        self.db_handler.write_data(self.log)

    def add_new_trade(self, newTrade):
        result = {"success": True, "message": "ok"}
        try:
            self.portfolio.add_entry_to_db(newTrade)
            self.portfolio.reload()
            self.livePricesThread.set_symbol_list(
                self.portfolio.get_holding_symbols())
        except Exception:
            result["success"] = False
            result["message"] = Messages.INVALID_OPERATION.value
        return result

    def set_auto_refresh(self, enabled):
        self.portfolio.livePricesThread.enable(enabled)

    def on_manual_refresh_live_data(self):
        if self.livePricesThread.is_enabled():
            self.livePricesThread.cancel_timeout()
        else:
            self.livePricesThread.force_single_run()

    def save_log_file(self, filepath):
        result = {"success": True, "message": "ok"}
        try:
            self.db_handler.write_data(self.log, filepath=filepath)
        except Exception:
            result["success"] = False
            result["message"] = Messages.ERROR_SAVE_FILE
        return result

    def open_log_file(self, filepath):
        result = {"success": True, "message": "ok"}
        try:
            self._reset(filepath)
        except Exception:
            result["success"] = False
            result["message"] = Messages.ERROR_OPEN_FILE
        return result

    def delete_last_trade(self):
        result = {"success": True, "message": "ok"}
        try:
            self.portfolio.remove_last_log_entry()
        except Exception:
            result["success"] = False
            result["message"] = Messages.INVALID_OPERATION
        self.portfolio.reload()
        self.livePricesThread.set_symbol_list(
            self.portfolio.get_holding_symbols())
        return result
