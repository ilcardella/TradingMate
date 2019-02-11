import os
import inspect
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

class Holding():

    def __init__(self, symbol, quantity, open_price=None):
        if quantity is None or quantity < 1:
            raise ValueError("Invalid quantity")
        if open_price is not None and open_price < 0:
            raise ValueError('Invalid open_price')
        self._symbol = symbol
        self._quantity = quantity
        self._openPrice = open_price
        self._lastPrice = None
        self._lastPriceValid = False

    def set_last_price(self, price):
        if price is None or price < 0:
            raise ValueError("Invalid price")
        self._lastPrice = price
        self._lastPriceValid = True

    def set_open_price(self, price):
        if price is None or price < 0:
            raise ValueError("Invalid price")
        self._openPrice = price

    def set_quantity(self, value):
        if value is None or value < 1:
            raise ValueError("Invalid quantity")
        self._quantity = value

    def add_quantity(self, value):
        """
        Add or subtract (if value is negative) the value to the holding quantity
        """
        self._quantity += value

    def set_last_price_invalid(self):
        self._lastPriceValid = False

    def get_symbol(self):
        return self._symbol

    def get_last_price(self):
        return self._lastPrice

    def get_open_price(self):
        return self._openPrice

    def get_quantity(self):
        return self._quantity

    def get_cost(self):
        if self._openPrice is None:
            return None
        return self._quantity * (self._openPrice/100) # £

    def get_value(self):
        if self._lastPrice is None:
            return None
        return self._quantity * (self._lastPrice/100) # £

    def get_profit_loss(self):
        value = self.get_value()
        cost = self.get_cost()
        if value is None or cost is None:
            return None
        return value - cost

    def get_profit_loss_perc(self):
        pl = self.get_profit_loss()
        cost = self.get_cost()
        if pl is None or cost is None:
            return None
        return (self.get_profit_loss() / self.get_cost()) * 100

    def get_last_price_valid(self):
        return self._lastPriceValid
