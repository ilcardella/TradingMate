import os
import sys
import inspect
import logging

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils
from Utils.Trade import Trade


class DatabaseHandler:
    """
    Handles the IO operation with the database to handle persistent data
    """

    def __init__(self, config, trading_log_path):
        """
        Initialise
        """
        self.db_filepath = trading_log_path
        self.db_name = "unknown"
        self.trading_history = []
        self.read_data(self.db_filepath)

    def read_data(self, filepath=None):
        """
        Read the trade history from the json database and return the list of trades

            - **filepath**: optional, if not set the configured path will be used
        """
        path = filepath if filepath is not None else self.db_filepath
        logging.info("DatabaseHandler - reading data from {}".format(path))
        self.db_filepath = path
        json_obj = Utils.load_json_file(path)
        # Store the database name
        self.db_name = json_obj["name"]
        # Create a list of all the trades in the json file
        self.trading_history.clear()
        if json_obj is not None:
            for item in json_obj["trades"]:
                trade = Trade.from_dict(item)
                self.trading_history.append(trade)

    def write_data(self, filepath=None):
        """
        Write the trade history to the database
        """
        path = filepath if filepath is not None else self.db_filepath
        logging.info("DatabaseHandler - writing data to {}".format(path))
        # Create a json object and store the trade history into it
        json_obj = {"name": self.db_name, "trades": []}
        for t in self.trading_history:
            json_obj["trades"].append(t.to_dict())
        # Write to file
        return Utils.write_json_file(path, json_obj)

    def get_db_filepath(self):
        """
        Return the database filepath
        """
        return self.db_filepath

    def get_trading_log_name(self):
        """
        Return the trading log database name
        """
        return self.db_name

    def get_trades_list(self):
        """
        Return the list of trades stored in the db
        """
        return self.trading_history

    def add_trade(self, trade):
        """
        Add a trade to the database
        """
        try:
            self.trading_history.append(trade)
        except Exception as e:
            logging.error(e)
            raise RuntimeError("Unable to add trade to the database")

    def remove_last_trade(self):
        """
        Remove the last trade from the trade history
        """
        try:
            del self.trading_history[-1]
        except Exception as e:
            logging.error(e)
            raise RuntimeError("Unable to delete last trade")
