import os
import sys
import inspect
import logging

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.TaskThread import TaskThread


class DataInterface(TaskThread):
    """Thread that periodically requests the most recent data from TradingMate
    server notify the parent object through a callback function"""

    def __init__(self, client, data_callback):
        TaskThread.__init__(self)
        self.client = client
        self._data_callback = data_callback
        # This interval determines how often the UI is updated
        self._interval = 10

    def task(self):
        # Get the portfolios and for each of them update their UI
        for pf in self.client.get_portfolios():
            self._data_callback(pf)
