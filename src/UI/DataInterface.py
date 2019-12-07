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

    def __init__(self, server, data_callback):
        TaskThread.__init__(self)
        self._server = server
        self._data_callback = data_callback
        # This interval determines how often the UI is updated
        self._interval = 5

    def task(self):
        # Get the portfolios and for each of them update their UI
        for pf in self._server.get_portfolios():
            self._data_callback(pf)

