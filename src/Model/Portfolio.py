import os
import inspect
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from .Holding import Holding

class Portfolio():
    def __init__(self, name):
        self._name = name
        self._cashAvailable = 0
        self._investedAmount = 0
        self._holdingsValue = 0
        self._holdings = {} # Dict {"symbol": Holding}

# PRIVATE FUNCTIONS

    def _update_holdings_value(self):
        """Compute the portfolio profit and loss"""
        self._holdingsValue = 0
        for holding in self._holdings.values():
            self._holdingsValue += holding.get_value()

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
        return self._holdings[symbol].get_last_price()

    def get_holding_open_price(self, symbol):
        """Return the last price for the given symbol"""
        return self._holdings[symbol].get_open_price()

    def get_total_value(self):
        """Return the value of the whole portfolio as cash + holdings"""
        return self._cashAvailable + self._holdingsValue

    def get_holdings_value(self):
        """Return the value of the holdings held in the portfolio"""
        return self._holdingsValue

    def get_portfolio_pl(self):
        """Return the profit/loss in £ of the portfolio over the invested amount"""
        return self.get_total_value() - self.get_invested_amount()

    def get_portfolio_pl_perc(self):
        """Return the profit/loss in % of the portfolio over the invested amount"""
        return (self.get_portfolio_pl() * 100) / self.get_invested_amount()

    def get_open_positions_pl(self):
        """Return the sum profit/loss in £ of the current open positions"""
        sum = 0
        for holding in self._holdings.values():
            sum += holding.get_profit_loss()
        return sum

    def get_open_positions_pl_perc(self):
        """Return the sum profit/loss in % of the current open positions"""
        costSum = 0
        valueSum = 0
        for holding in self._holdings.values():
            costSum += holding.get_cost()
            valueSum += holding.get_value()
        return ((valueSum - costSum) / costSum) * 100

# SETTERS

    def set_cash_available(self, value):
        self._cashAvailable = value

    def set_invested_amount(self, value):
        self._investedAmount = value

# FUNCTIONS

    def clear(self):
        """Clear all data in the portfolio to default values"""
        self._cashAvailable = 0
        self._investedAmount = 0
        self._holdingsValue = 0
        self._holdings.clear()

    def update_holding_amount(self, symbol, amount):
        if symbol in self._holdings:
            if amount < 1:
                del self._holdings[symbol]
            else:
                self._holdings[symbol].set_amount(amount)
        else:
            self._holdings[symbol] = Holding(symbol, amount)
        self._update_holdings_value()

    def update_holding_last_price(self, symbol, price):
        if symbol in self._holdings:
            self._holdings[symbol].set_last_price(price)
            self._update_holdings_value()

    def update_holding_open_price(self, symbol, price):
        if symbol in self._holdings:
            self._holdings[symbol].set_open_price(price)

# END CLASS
