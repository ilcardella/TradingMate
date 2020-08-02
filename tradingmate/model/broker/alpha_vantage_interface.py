import logging
import sys
import time
import traceback
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional

from alpha_vantage.timeseries import TimeSeries

from ...utils import Markets
from .. import ConfigurationManager
from . import StocksInterface

AVJSONData = Dict[str, Dict[str, str]]


class AVInterval(Enum):
    """
    AlphaVantage interval types: '1min', '5min', '15min', '30min', '60min',
    'daily', 'weekly' and 'monthly'
    """

    MIN_1 = "1min"
    MIN_5 = "5min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    MIN_60 = "60min"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AlphaVantageInterface(StocksInterface):
    """class providing interfaces to request data from AlphaVantage"""

    _config: ConfigurationManager
    _last_call_ts: datetime
    _TS: TimeSeries

    def __init__(self, config: ConfigurationManager) -> None:
        self._config = config
        self._last_call_ts = datetime.now()
        self._TS = TimeSeries(
            key=config.get_alpha_vantage_api_key(),
            output_format="json",
            treat_info_as_error=True,
        )
        logging.info("AlphaVantageInterface initialised")

    def _daily(self, market_id: str) -> Optional[AVJSONData]:
        """
        Calls AlphaVantage API and return the Daily time series for the given market

            - **market_id**: string representing a market ticker
            - Returns **None** if an error occurs otherwise the pandas dataframe
        """
        try:
            market_id = self._format_market_id(market_id)
            data, meta_data = self._TS.get_daily(symbol=market_id, outputsize="compact")
            return data
        except Exception as e:
            logging.error("AlphaVantage wrong api call for {}".format(market_id))
            logging.debug(e)
            logging.debug(traceback.format_exc())
            logging.debug(sys.exc_info()[0])
        return None

    def _format_market_id(self, market_id: str) -> str:
        """
        Convert a standard market id to be compatible with AlphaVantage API.
        Adds the market exchange prefix (i.e. London is LON:)
        """
        if f"{Markets.LSE.value}:" in market_id:
            market_id = market_id.replace(f"{Markets.LSE.value}", "LON")
        return market_id

    def _wait_before_call(self) -> None:
        """
        Wait between API calls to not overload the server
        """
        while (datetime.now() - self._last_call_ts) <= timedelta(
            seconds=self._config.get_alpha_vantage_polling_period()
        ):
            time.sleep(0.2)
        self._last_call_ts = datetime.now()

    def get_last_close_price(self, market_id: str) -> Optional[float]:
        interval: AVInterval = AVInterval.DAILY
        prices = self.get_prices(market_id, interval)
        if prices is None:
            return None
        last = next(iter(prices.values()))
        return float(last["4. close"])

    def get_prices(
        self, market_id: str, interval: AVInterval = AVInterval.DAILY
    ) -> Optional[AVJSONData]:
        """
        Return the price time series of the requested market with the interval
        granularity. Return None if the interval is invalid
        """
        self._wait_before_call()
        if interval == AVInterval.DAILY:
            return self._daily(market_id)
        else:
            logging.warning(
                "AlphaVantageInterface supports only DAILY interval. Requested interval: {}".format(
                    interval.value
                )
            )
            raise ValueError(f"Invalid AVInterval value: {interval.name}")
