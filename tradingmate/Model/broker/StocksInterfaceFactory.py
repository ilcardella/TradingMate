import os
import sys
import inspect

from .YFinanceInterface import YFinanceInterface
from .AlphaVantageInterface import AlphaVantageInterface


class StocksInterfaceFactory:
    """Factory for stocks interface class"""

    def __init__(self, config):
        self._config = config

    def make(self, value):
        if value == "yfinance":
            return YFinanceInterface(self._config)
        elif value == "alpha_vantage":
            return AlphaVantageInterface(self._config)
        else:
            raise ValueError("Stock interface not supported: {}".format(value))

    def make_from_configuration(self):
        return self.make(self._config.get_configured_stocks_interface())