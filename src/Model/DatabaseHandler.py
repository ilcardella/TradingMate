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

class DatabaseHandler():
    """
    Handles the IO operation with the database to handle persistent data
    """
    def __init__(self, config):
        """
        Initialise
        """
        # By default use the configured filepath
        self.db_filepath = config.get_trading_database_path()
        # Create an empty list to store trades from database
        self.trading_history = []

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

        # Create a list of all the trades in the json file
        for item in json_obj['trades']:
            trade = Trade.from_dict(item)
            # Store the list internally
            self.trading_history.append(trade)


    def write_data(self, filepath=None):
        """
        Write the trade history to the database
        """
        path = filepath if filepath is not None else self.db_filepath

        # Create a json object to store the trade history into
        json_obj = {
            'trades': []
        }

        for t in self.trading_history:
            json_obj['trades'].append(t.to_dict())

        # Write to file
        return Utils.write_json_file(path, json_obj)

    def get_db_filepath(self):
        """
        Return the database filepath
        """
        return self.db_filepath

    def get_trades_list(self):
        """
        Return the list of trades stored in the db
        """
        return self.trading_history

    def add_trade(self, trade):
        """
        Add a trade to the database
        """
        self.trading_history.append(trade)

    def remove_last_trade(self):
        """
        Remove the last trade from the trade history
        """
        del self.trading_history[-1]
