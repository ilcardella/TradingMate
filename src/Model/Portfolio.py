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
        self._holdings = {} # Dict {"symbol": Holding}

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

# SETTERS

    def set_cash_available(self, value):
        if value is None or value < 0:
            raise ValueError('Invalid value for cash_available')
        self._cashAvailable = value

    def set_invested_amount(self, value):
        if value is None or value < 0:
            raise ValueError('Invalid value for investedAmount')
        self._investedAmount = value

# FUNCTIONS

    def clear(self):
        """Clear all data in the portfolio to default values"""
        self._cashAvailable = 0
        self._investedAmount = 0
        self._holdings.clear()

    def update_holding_amount(self, symbol, amount):
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
        if symbol in self._holdings:
            self._holdings[symbol].set_open_price(price)
        else:
            raise ValueError('Invalid symbol')

    def add_trade(self, trade):
        # TODO
        # Add logic of function PortfolioManager::_update_portfolio() here
        # Integrate with functions update_xxx() above and remove if necessary
        raise NotImplementedError()

# END CLASS
