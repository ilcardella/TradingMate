import os
import sys
import inspect
import requests
import json
import logging

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.TaskThread import TaskThread
from Utils.ConfigurationManager import ConfigurationManager
from Utils.Utils import Markets


class StockPriceGetter(TaskThread):
    def __init__(self, config, onNewPriceDataCallback):
        TaskThread.__init__(self)
        self.config = config
        self.onNewPriceDataCallback = onNewPriceDataCallback
        self.reset()
        logging.info("StockPriceGetter initialised")

    def _read_configuration(self):
        # Override the parent class default value
        self._interval = self.config.get_alpha_vantage_polling_period()

    def task(self):
        priceDict = {}
        for symbol in self.symbolList:
            if not self._finished.isSet():
                value = self._fetch_price_data(symbol)
                # Wait as suggested by AlphaVantage support
                self._timeout.wait(2)
                if value is not None:
                    priceDict[symbol] = value
        if not self._finished.isSet():
            self.lastData = priceDict  # Store internally
            self.onNewPriceDataCallback()  # Notify the model

    def _fetch_price_data(self, symbol):
        # TODO use alpha_vantage lib instead of manual request
        try:
            url = self._build_url(
                "TIME_SERIES_DAILY",
                symbol,
                "5min",
                self.config.get_alpha_vantage_api_key(),
            )
        except Exception as e:
            logging.error(e)
            logging.error(
                "StockPriceGetter - Unable to build url for {}".format(symbol)
            )
            return None
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logging.error(
                    "StockPriceGetter - Request for {} returned code {}".format(
                        url.split("apikey")[0], response.status_code
                    )
                )
                return None
            data = json.loads(response.text)
            timeSerie = data["Time Series (Daily)"]
            last = next(iter(timeSerie.values()))
            value = float(last["4. close"])
        except Exception:
            logging.error(
                "StockPriceGetter - Unable to fetch data from {}".format(
                    url.split("apikey")[0]
                )
            )
            value = None
        return value

    def _build_url(self, aLength, aSymbol, anInterval, anApiKey):
        function = "function={}".format(aLength)
        symbol = "symbol={}".format(self.convert_market_to_alphavantage(aSymbol))
        apiKey = "apikey={}".format(anApiKey)
        return "{}?{}&{}&{}".format(
            self.config.get_alpha_vantage_base_url(), function, symbol, apiKey
        )

    def convert_market_to_alphavantage(self, symbol):
        """
        Convert the market (LSE, etc.) into the alphavantage market compatible string
        i.e.: the LSE needs to be converted to LON
        """
        # Extract the market part from the symbol string
        market = str(symbol).split(":")[0]
        av_market = Markets[market]
        return "{}:{}".format(av_market.value, str(symbol).split(":")[1])

    def get_last_data(self):
        return self.lastData

    def set_symbol_list(self, aList):
        self.symbolList = aList

    def reset(self):
        self._read_configuration()
        self.lastData = {}
        self.symbolList = []
