import os
import inspect
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from .Holding import Holding
from Utils.Utils import Actions, Messages, Callbacks
from .StockPriceGetter import StockPriceGetter
from .DatabaseHandler import DatabaseHandler

class Portfolio():
    def __init__(self, name, config):
        # Portfolio name
        self._name = name
        # Amount of free cash available
        self._cashAvailable = 0
        # Overall amount of cash deposited - withdrawed
        self._investedAmount = 0
        # Data structure to store stock holdings: {"symbol": Holding}
        self._holdings = {}
        # In memory database of trades history
        self.trading_history = {}
        # Work thread that fetches stocks live prices
        self.livePricesThread = StockPriceGetter(config, self.on_new_price_data)
        # Database handler
        self.db_handler = DatabaseHandler(config)
        # DataStruct containing the callbacks
        self.callbacks = {}

    def start(self):
        # TODO move in init and remove this function
        self.trading_history = self.db_handler.read_data()
        self.reload()
        self.livePricesThread.set_symbol_list(self.get_holding_symbols())
        self.livePricesThread.start()

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def stop_application(self):
        self.livePricesThread.shutdown()
        self.livePricesThread.join()
        self.db_handler.write_data(self.trading_history)

# GETTERS

    def get_name(self):
        """Return the portfolio name [string]"""
        return self._name

    def get_cash_available(self):
        """Return the available cash amount in the portfolio [int]"""
        return self._cashAvailable

    def get_invested_amount(self):
        """Return the total invested amount in the portfolio [int]"""
        return self._investedAmount

    def get_holding_list(self):
        """Return a list of Holding instances held in the portfolio sorted alphabetically"""
        return [self._holdings[k] for k in sorted(self._holdings)]

    def get_holding_symbols(self):
        """Return a list containing the holding symbols as [string] sorted alphabetically"""
        return list(sorted(self._holdings.keys()))

    def get_holding_amount(self, symbol):
        """Return the amount held for the given symbol"""
        if symbol in self._holdings:
            return self._holdings[symbol].get_amount()
        else:
            return 0

    def get_holding_last_price(self, symbol):
        """Return the last price for the given symbol"""
        if symbol not in self._holdings:
            raise ValueError('Invalid symbol')
        return self._holdings[symbol].get_last_price()

    def get_holding_open_price(self, symbol):
        """Return the last price for the given symbol"""
        if symbol not in self._holdings:
            raise ValueError('Invalid symbol')
        return self._holdings[symbol].get_open_price()

    def get_total_value(self):
        """Return the value of the whole portfolio as cash + holdings"""
        value = self.get_holdings_value()
        if value is not None:
            return self._cashAvailable + value
        else:
            return None

    def get_holdings_value(self):
        """Return the value of the holdings held in the portfolio"""
        holdingsValue = 0
        for holding in self._holdings.values():
            if holding.get_value() is not None:
                holdingsValue += holding.get_value()
            else:
                return None
        return holdingsValue

    def get_portfolio_pl(self):
        """Return the profit/loss in £ of the portfolio over the invested amount"""
        value = self.get_total_value()
        invested = self.get_invested_amount()
        if value is None or invested is None:
            return None
        return value - invested

    def get_portfolio_pl_perc(self):
        """Return the profit/loss in % of the portfolio over the invested amount"""
        pl = self.get_portfolio_pl()
        invested = self.get_invested_amount()
        if pl is None or invested is None or invested < 1:
            return None
        return (pl / invested) * 100

    def get_open_positions_pl(self):
        """Return the sum profit/loss in £ of the current open positions"""
        sum = 0
        for holding in self._holdings.values():
            pl = holding.get_profit_loss()
            if pl is None:
                return None
            sum += pl
        return sum

    def get_open_positions_pl_perc(self):
        """Return the sum profit/loss in % of the current open positions"""
        costSum = 0
        valueSum = 0
        for holding in self._holdings.values():
            cost = holding.get_cost()
            value = holding.get_value()
            if cost is None or value is None:
                return None
            costSum += cost
            valueSum += value
        if costSum < 1:
            return None
        return ((valueSum - costSum) / costSum) * 100

    def get_db_filepath(self):
        return self.db_handler.get_db_filepath()

    def get_log_as_list(self):
        return self.trading_history['trades']

# SETTERS

    def set_cash_available(self, value):
        if value is None or value < 0:
            raise ValueError('Invalid value for cash_available')
        self._cashAvailable = value

    def set_invested_amount(self, value):
        if value is None or value < 0:
            raise ValueError('Invalid value for investedAmount')
        self._investedAmount = value

    def set_auto_refresh(self, enabled):
        self.livePricesThread.enable(enabled)

# FUNCTIONS

    def clear(self):
        """Clear all data in the portfolio to default values"""
        self._cashAvailable = 0
        self._investedAmount = 0
        self._holdings.clear()

    def update_holding_amount(self, symbol, amount):
        # TODO remove this and fix unit test
        if symbol in self._holdings:
            if amount < 1:
                del self._holdings[symbol]
            else:
                self._holdings[symbol].set_amount(amount)
        else:
            self._holdings[symbol] = Holding(symbol, amount)

    def update_holding_last_price(self, symbol, price):
        if symbol in self._holdings:
            self._holdings[symbol].set_last_price(price)
        else:
            raise ValueError('Invalid symbol')

    def update_holding_open_price(self, symbol, price):
        # TODO remove this and fix unit test
        if symbol in self._holdings:
            self._holdings[symbol].set_open_price(price)
        else:
            raise ValueError('Invalid symbol')

    def reload(self):
        """
        Read each trade from the database and load the portfolio
        """
        # Reset the portfolio
        self.clear()

        for trade in self.trading_history['trades']:
            action = trade['action']
            amount = float(trade['amount'])
            symbol = trade['symbol'] if 'symbol' in trade else None
            price = float(trade['price'])
            fee = float(trade['fee'])
            sd = float(trade['stamp_duty'])

            if action == Actions.DEPOSIT.name or action == Actions.DIVIDEND.name:
                self._cashAvailable += amount
                if action == Actions.DEPOSIT.name:
                    self._investedAmount += amount
            elif action == Actions.WITHDRAW.name:
                self._cashAvailable -= amount
                self._investedAmount -= amount
            elif action == Actions.BUY.name:
                if symbol not in self._holdings:
                    self._holdings[symbol] = Holding(symbol, amount)
                else:
                    self._holdings[symbol].add_quantity(amount)
                cost = (price/100) * amount
                tax = (sd * cost) / 100
                totalCost = cost + tax + fee
                self._cashAvailable -= totalCost
            elif action == Actions.SELL.name:
                self._holdings[symbol].add_quantity(-amount) # negative
                if self._holdings[symbol].get_amount() < 1:
                    del self._holdings[symbol]
                profit = ((price/100) * amount) - fee
                self._cashAvailable += profit

        for symbol in self._holdings.keys():
            self._holdings[symbol].set_open_price(self.compute_avg_holding_open_price(symbol))
        for symbol, price in self.livePricesThread.get_last_data().items():
            self._holdings[symbol].set_last_price(price)

    def compute_avg_holding_open_price(self, symbol):
        """
        Return the average price paid to open the current positon of the requested stock.
        Starting from the end of the history log, find the BUY transaction that led to
        to have the current amount, compute then the average price of these transactions
        """
        sum = 0
        count = 0
        targetAmount = self.get_holding_amount(symbol)
        for trade in self.trading_history['trades'][::-1]:  # reverse order
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

    def add_trade(self, trade):
        result = {"success": True, "message": "ok"}
        try:
            self.add_entry_to_db(trade)
            self.reload_portfolio()
            self.livePricesThread.set_symbol_list(self.get_holding_symbols())
        except Exception:
            result["success"] = False
            result["message"] = Messages.INVALID_OPERATION.value
        return result

    def is_trade_valid(self, newTrade):
        result = {"success": True, "message": "ok"}

        if newTrade["action"] == Actions.WITHDRAW.name:
            if newTrade["amount"] > self.get_cash_available():
                result["success"] = False
                result["message"] = Messages.INSUF_FUNDING.value
        elif newTrade["action"] == Actions.BUY.name:
            cost = (newTrade["price"] * newTrade["amount"]) / 100  # in £
            fee = newTrade["fee"]
            tax = (newTrade["stamp_duty"] * cost) / 100
            totalCost = cost + fee + tax
            if totalCost > self.get_cash_available():
                result["success"] = False
                result["message"] = Messages.INSUF_FUNDING.value
        elif newTrade["action"] == Actions.SELL.name:
            if newTrade["amount"] > self.get_holding_amount(newTrade["symbol"]):
                result["success"] = False
                result["message"] = Messages.INSUF_HOLDINGS.value
        return result

# EVENTS

    def on_new_price_data(self):
        priceDict = self.livePricesThread.get_last_data()
        for symbol, price in priceDict.items():
            self.update_holding_last_price(symbol, price)
        self.callbacks[Callbacks.UPDATE_LIVE_PRICES]()

    def on_manual_refresh_live_data(self):
        if self.livePricesThread.is_enabled():
            self.livePricesThread.cancel_timeout()
        else:
            self.livePricesThread.force_single_run()

# DATABASE OPERATION

    def add_entry_to_db(self, logEntry):
        """
        Add a new trade into the trade history database
        """
        if 'trades' in self.trading_history:
            self.trading_history['trades'].append(logEntry)
        else:
            self.trading_history['trades'] = []
            self.trading_history['trades'].append(logEntry)

    def delete_last_trade(self):
        """
        Delete the last trade from the trade history database
        """
        result = {"success": True, "message": "ok"}
        try:
            del self.trading_history['trades'][-1]
        except Exception:
            result["success"] = False
            result["message"] = Messages.INVALID_OPERATION
        self.reload()
        self.livePricesThread.set_symbol_list(self.get_holding_symbols())
        return result

    def save_log_file(self, filepath):
        result = {"success": True, "message": "ok"}
        try:
            self.db_handler.write_data(self.trading_history, filepath=filepath)
        except Exception:
            result["success"] = False
            result["message"] = Messages.ERROR_SAVE_FILE
        return result

    def open_log_file(self, filepath):
        result = {"success": True, "message": "ok"}
        try:
            self.db_handler.read_data(filepath)
            self.reload()
        except Exception:
            result["success"] = False
            result["message"] = Messages.ERROR_OPEN_FILE
        return result

# END CLASS
