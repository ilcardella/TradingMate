from typing import Callable, List

from ..model import Portfolio
from ..utils import TaskThread
from . import TradingMateClient


class DataInterface(TaskThread):
    """Thread that periodically requests the most recent data from TradingMate
    server notify the parent object through a callback function"""

    _client: TradingMateClient
    _data_callback: Callable[[List[Portfolio]], None]
    _interval: int = 1

    def __init__(
        self,
        client: TradingMateClient,
        data_callback: Callable[[List[Portfolio]], None],
    ):
        TaskThread.__init__(self)
        self._client = client
        self._data_callback = data_callback  # type: ignore
        # This interval determines how often the UI is updated
        self._interval = 1

    def task(self):
        # Get the portfolios and call the callback to update the UI
        self._data_callback(self._client.get_portfolios())
