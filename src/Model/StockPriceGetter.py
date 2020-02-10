import os
import sys
import inspect
import logging

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.TaskThread import TaskThread
from Utils.ConfigurationManager import ConfigurationManager
from .broker.StocksInterfaceFactory import StocksInterfaceFactory


class StockPriceGetter(TaskThread):
    def __init__(self, config, update_callback):
        super(StockPriceGetter, self).__init__()
        self._config = config
        self._price_update_callback = update_callback
        self.reset()
        self._stock_ifc = StocksInterfaceFactory(config).make_from_configuration()
        self._interval = config.get_polling_period()

    def task(self):
        priceDict = {}
        for symbol in self.symbolList:
            if not self._finished.isSet():
                value = self._fetch_price_data(symbol)
                if value is not None:
                    priceDict[symbol] = value
        if not self._finished.isSet():
            self.lastData = priceDict  # Store internally
            self._price_update_callback()  # Notify the model

    def _fetch_price_data(self, symbol):
        try:
            value = self._stock_ifc.get_last_close_price(symbol)
            assert value is not None
        except Exception as e:
            logging.error(
                "StockPriceGetter - Unable to fetch data for {}: {}".format(symbol, e)
            )
            value = None
        return value

    def get_last_data(self):
        return self.lastData

    def set_symbol_list(self, aList):
        self.symbolList = aList

    def reset(self):
        self.lastData = {}
        self.symbolList = []
