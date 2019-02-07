import os
import sys
import inspect
import logging

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils
from Utils.Trade import Trade
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

    def read_data(self, filepath=None):
        """
        Read the trade history from the json database and return the list of trades

            - **filepath**: optional, if not set the configured path will be used
        """
        path = filepath if filepath is not None else self.db_filepath
        self.db_filepath = path
        json_obj = Utils.load_json_file(path)

        if 'trades' not in json_obj:
            raise Exception('Database wrong format: trade key missing')

        # Read
        trades = []
        for item in json_obj['trades']:
            trade = Trade.from_dict(item)
            trades.append(trade)
        return trades


    def write_data(self, trades, filepath=None):
        """
        Write the trade history to the database
        """
        path = filepath if filepath is not None else self.db_filepath

        # Create a json object to store the trade history into
        json_obj = {
            'trades': []
        }

        for t in trades:
            json_obj['trades'].append(t.to_dict())

        # Write to file
        return Utils.write_json_file(path, json_obj)

    def get_db_filepath(self):
        """
        Return the database filepath
        """
        return self.db_filepath
