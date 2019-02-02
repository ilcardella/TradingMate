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
        # Class to collect stocks live prices
        self.livePricesThread = StockPriceGetter(config, self.on_new_price_data)
        # Database handler
        self.db_handler = DatabaseHandler(config)
        # Portfolio instance
        self.portfolio = Portfolio("Portfolio1")

# INTERNAL FUNCTIONS

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def _read_configuration(self, config):
        pass

    def _update_portfolio(self):
        """
        Scan the database and update the Portfolio instance
        """
        cashAvailable = 0.0
        investedAmount = 0.0
        holdings = {}
        for trade in self.log['trades']:
            action = trade['action']
            amount = float(trade['amount'])
            symbol = trade['symbol'] if 'symbol' in trade else None
            price = float(trade['price'])
            fee = float(trade['fee'])
            sd = float(trade['stamp_duty'])

            if action == Actions.DEPOSIT.name or action == Actions.DIVIDEND.name:
                cashAvailable += amount
                if action == Actions.DEPOSIT.name:
                    investedAmount += amount
            elif action == Actions.WITHDRAW.name:
                cashAvailable -= amount
                investedAmount -= amount
            elif action == Actions.BUY.name:
                if symbol not in holdings:
                    holdings[symbol] = amount
                else:
                    holdings[symbol] += amount
                cost = (price/100) * amount
                tax = (sd * cost) / 100
                totalCost = cost + tax + fee
                cashAvailable -= totalCost
            elif action == Actions.SELL.name:
                holdings[symbol] -= amount
                if holdings[symbol] < 1:
                    del holdings[symbol]
                profit = ((price/100) * amount) - fee
                cashAvailable += profit

        self.portfolio.clear()
        for symbol, amount in holdings.items():
            self.portfolio.update_holding_amount(symbol, amount)
            self.portfolio.update_holding_open_price(
                symbol, self.get_holding_open_price(symbol))
        self.portfolio.set_invested_amount(investedAmount)
        self.portfolio.set_cash_available(cashAvailable)
        for symbol, price in self.livePricesThread.get_last_data().items():
            self.portfolio.update_holding_last_price(symbol, price)

    def _add_entry_to_db(self, logEntry):
        if 'trades' in self.log:
            self.log['trades'].append(logEntry)
        else:
            self.log['trades'] = []
            self.log['trades'].append(logEntry)

    def _remove_last_log_entry(self):
        del self.log['trades'][-1]

    def _reset(self, filepath=None):
        self._read_configuration()
        self.db_handler.read_data(filepath)
        self._update_portfolio()

# GETTERS

    def get_log_as_list(self):
        return self.log['trades']

    def get_holding_open_price(self, symbol):
        """
        Return the average price paid to open the current positon of the requested stock.
        Starting from the end of the history log, find the BUY transaction that led to
        to have the current amount, compute then the average price of these transactions
        """
        sum = 0
        count = 0
        targetAmount = self.portfolio.get_holding_amount(symbol)
        for trade in self.log['trades'][::-1]:  # reverse order
            action = trade['action']
            sym = trade['symbol'] if 'symbol' in trade else None
            price = float(trade['price'])
            amount = float(trade['amount'])
            if sym == symbol and action == Actions.BUY.name:
                targetAmount -= amount
                sum += price * amount
                count += amount
                if targetAmount <= 0:
                    break
        avg = sum / count
        return round(avg, 4)

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
        self._update_portfolio()
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
            self._add_entry_to_db(newTrade)
            self._update_portfolio()
            self.livePricesThread.set_symbol_list(
                self.portfolio.get_holding_symbols())
        except Exception:
            result["success"] = False
            result["message"] = Messages.INVALID_OPERATION.value
        return result

    def on_new_price_data(self):
        priceDict = self.livePricesThread.get_last_data()
        for symbol, price in priceDict.items():
            self.portfolio.update_holding_last_price(symbol, price)
        self.callbacks[Callbacks.UPDATE_LIVE_PRICES]()  # Call callback

    def set_auto_refresh(self, enabled):
        self.livePricesThread.enable(enabled)

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
            self._remove_last_log_entry()
        except Exception:
            result["success"] = False
            result["message"] = Messages.INVALID_OPERATION
        self._update_portfolio()
        self.livePricesThread.set_symbol_list(
            self.portfolio.get_holding_symbols())
        return result
