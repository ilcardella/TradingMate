import logging
from typing import Callable, Dict, List, Optional

from ..utils import TaskThread
from . import ConfigurationManager
from .broker import StocksInterface, StocksInterfaceFactory


class StockPriceGetter(TaskThread):
    """Worker thread that fetches market live prices from an online source"""

    _config: ConfigurationManager
    _price_update_callback: Callable[[], None]
    _stock_ifc: StocksInterface
    _interval: float
    lastData: Dict[str, float] = {}
    symbolList: List[str]

    def __init__(
        self, config: ConfigurationManager, update_callback: Callable[[], None]
    ) -> None:
        super(StockPriceGetter, self).__init__()
        self._config = config
        self._price_update_callback = update_callback  # type: ignore
        self.reset()
        self._stock_ifc = StocksInterfaceFactory(config).make_from_configuration()
        self._interval = config.get_polling_period()

    def task(self) -> None:
        priceDict = {}
        for symbol in self.symbolList:
            if not self._finished.is_set():
                value = self._fetch_price_data(symbol)
                if value is not None:
                    priceDict[symbol] = value
        if not self._finished.is_set():
            self.lastData = priceDict
            # Notify the model
            self._price_update_callback()  # type: ignore

    def _fetch_price_data(self, symbol: str) -> Optional[float]:
        try:
            value = self._stock_ifc.get_last_close_price(symbol)
            assert value is not None
            return value
        except Exception as e:
            logging.error(
                "StockPriceGetter - Unable to fetch data for {}: {}".format(symbol, e)
            )
            return None

    def get_last_data(self) -> Dict[str, float]:
        return self.lastData

    def set_symbol_list(self, aList: List[str]) -> None:
        self.symbolList = aList

    def reset(self) -> None:
        self.lastData = {}
        self.symbolList = []
