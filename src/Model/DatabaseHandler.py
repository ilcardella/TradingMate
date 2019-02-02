import os
import sys
import inspect
import logging

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils
from Utils.ConfigurationManager import ConfigurationManager

class DatabaseHandler():
    """
    Handles the IO operation with the database to handle persistent data
    """

    def __init__(self, config):
        """
        Initialise
        """
        self.db_filepath = config.get_trading_database_path()
        self.trading_log = self.read_data()

    def read_data(self, filepath=None):
        """
        Read data from database and return a dict

            - **filepath**: optional, if not set the configured path will be used
        """
        path = filepath if filepath is not None else self.db_filepath
        self.db_filepath = path
        return Utils.load_json_file(path)

    def write_data(self, data, filepath=None):
        """
        Write data to the database
        """
        path = filepath if filepath is not None else self.db_filepath
        return Utils.write_json_file(path, data)

    def get_db_filepath(self):
        """
        Return the database filepath
        """
        return self.db_filepath
