import os
import sys
import inspect
import logging
from enum import Enum
import datetime as dt
import time
import yfinance as yf

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Markets
from .StocksInterface import StocksInterface


class YFInterval(Enum):
    MIN_1 = "1m"
    MIN_2 = "2m"
    MIN_5 = "5m"
    MIN_15 = "15"
    MIN_30 = "30m"
    MIN_60 = "60m"
    MIN_90 = "90m"
    HOUR = "1h"
    DAY_1 = "1d"
    DAY_5 = "5d"
    WEEK_1 = "1wk"
    MONTH_1 = "1mo"
    MONTH_3 = "3mo"


class YFinanceInterface(StocksInterface):
    def __init__(self, config):
        self._config = config
        self._last_call_ts = dt.datetime(1, 1, 1)
        logging.info("YFinanceInterface created")

    def _format_market_id(self, market_id):
        if f"{Markets.LSE.value}:" in market_id:
            market_id = market_id.replace(f"{Markets.LSE.value}:", "") + ".L"
        return market_id

    def _wait_before_call(self):
        """
        Wait between API calls to not overload the server
        """
        while (dt.datetime.now() - self._last_call_ts) <= dt.timedelta(
            seconds=self._config.get_yfinance_polling_period()
        ):
            time.sleep(0.1)
        self._last_call_ts = dt.datetime.now()

    def get_last_close_price(self, market_id, interval=YFInterval.HOUR):
        self._wait_before_call()
        ticker = yf.Ticker(self._format_market_id(market_id))
        data = ticker.history(period="1d", interval=interval.value)
        return data["Close"].iloc[0] if data is not None else None
