import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

import yfinance as yf

from ...utils import Markets
from .. import ConfigurationManager
from . import StocksInterface


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

    config: ConfigurationManager
    _last_call_ts: datetime

    def __init__(self, config: ConfigurationManager):
        self._config = config
        self._last_call_ts = datetime(1, 1, 1)
        logging.info("YFinanceInterface created")

    def _format_market_id(self, market_id: str) -> str:
        if f"{Markets.LSE.value}:" in market_id:
            market_id = market_id.replace(f"{Markets.LSE.value}:", "") + ".L"
        return market_id

    def _wait_before_call(self) -> None:
        """
        Wait between API calls to not overload the server
        """
        while (datetime.now() - self._last_call_ts) <= timedelta(
            seconds=self._config.get_yfinance_polling_period()
        ):
            time.sleep(0.1)
        self._last_call_ts = datetime.now()

    def get_last_close_price(self, market_id: str) -> Optional[float]:
        interval: YFInterval = YFInterval.HOUR
        self._wait_before_call()
        ticker = yf.Ticker(self._format_market_id(market_id))
        data = ticker.history(period="1d", interval=interval.value)
        return data["Close"].iloc[0] if data is not None else None

    def get_market_details(self, market_ticker: str) -> Dict[str, Any]:
        self._wait_before_call()
        ticker = yf.Ticker(self._format_market_id(market_ticker))
        return {
            "dividends": ticker.dividends,
            "info": ticker.info,
            "calendar": ticker.calendar,
            "earnings": ticker.earnings,
            "financials": ticker.financials,
            "balance_sheet": ticker.balance_sheet,
            "cashflow": ticker.cashflow,
        }
