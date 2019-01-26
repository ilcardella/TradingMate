import os
import inspect
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

class Holding():

    def __init__(self, symbol, amount, open_price=None):
        self._symbol = symbol
        self._amount = amount
        self._openPrice = open_price
        self._lastPrice = None
        self._lastPriceValid = False

    def set_last_price(self, price):
        self._lastPrice = price
        self._lastPriceValid = True

    def set_open_price(self, price):
        self._openPrice = price

    def set_amount(self, value):
        self._amount = value

    def set_last_price_invalid(self):
        self._lastPriceValid = False

    def get_symbol(self):
        return self._symbol

    def get_last_price(self):
        return self._lastPrice

    def get_open_price(self):
        return self._openPrice

    def get_amount(self):
        return self._amount

    def get_cost(self):
        return self._amount * (self._openPrice/100) # £

    def get_value(self):
        return self._amount * (self._lastPrice/100) # £

    def get_profit_loss(self):
        return (self.get_value() - self.get_cost())

    def get_profit_loss_perc(self):
        return (self.get_profit_loss() * 100) / self.get_cost()

    def get_last_price_valid(self):
        return self._lastPriceValid
