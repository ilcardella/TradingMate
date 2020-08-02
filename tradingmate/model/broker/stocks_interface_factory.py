from typing import Union

from .. import ConfigurationManager
from . import AlphaVantageInterface, YFinanceInterface

# StocksInterfaceImpl = TypeVar("StocksInterfaceImpl", bound=StocksInterface)
StocksInterfaceImpl = Union[AlphaVantageInterface, YFinanceInterface]


class StocksInterfaceFactory:
    """Factory for stocks interface class"""

    _config: ConfigurationManager

    def __init__(self, config: ConfigurationManager):
        self._config = config

    def make(self, value: str) -> StocksInterfaceImpl:
        if value == "yfinance":
            return YFinanceInterface(self._config)
        elif value == "alpha_vantage":
            return AlphaVantageInterface(self._config)
        else:
            raise ValueError("Stock interface not supported: {}".format(value))

    def make_from_configuration(self) -> StocksInterfaceImpl:
        return self.make(self._config.get_configured_stocks_interface())
