import logging
from pathlib import Path
from typing import Any, List

from ..utils import Utils
from . import ConfigurationManager, Trade


class DatabaseHandler:
    """
    Handles the IO operation with the database to handle persistent data
    """

    db_filepath: Path
    db_name: str = "unknown"
    trading_history: List[Trade]

    def __init__(self, config: ConfigurationManager, trading_log_path: Path) -> None:
        """
        Initialise
        """
        self.db_filepath = trading_log_path
        self.db_name = "unknown"
        self.trading_history = []
        self.read_data(self.db_filepath)

    def read_data(self, filepath: Path = None):
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
        self.trading_history = sorted(self.trading_history, key=lambda t: t.date)

    def write_data(self, filepath: Path = None) -> bool:
        """
        Write the trade history to the database
        """
        path = filepath if filepath is not None else self.db_filepath
        logging.info("DatabaseHandler - writing data to {}".format(path))
        # Create a json object and store the trade history into it
        json_obj: Any = {
            "name": self.db_name,
            "trades": [],
        }
        for t in self.trading_history:
            json_obj["trades"].append(t.to_dict())
        # Write to file
        return Utils.write_json_file(path, json_obj)

    def get_db_filepath(self) -> Path:
        """
        Return the database filepath
        """
        return self.db_filepath

    def get_trading_log_name(self) -> str:
        """
        Return the trading log database name
        """
        return self.db_name

    def get_trades_list(self) -> List[Trade]:
        """
        Return the list of trades stored in the db
        """
        return self.trading_history

    def add_trade(self, trade: Trade) -> None:
        """
        Add a trade to the database
        """
        try:
            self.trading_history.append(trade)
            self.trading_history = sorted(self.trading_history, key=lambda t: t.date)
        except Exception as e:
            logging.error(e)
            raise RuntimeError("Unable to add trade to the database")

    def delete_trade(self, trade_id: str) -> None:
        """
        Remove the trade from the trade history
        """
        try:
            item = next((t for t in self.trading_history if t.id == trade_id))
            self.trading_history.remove(item)
        except Exception as e:
            logging.error(e)
            raise RuntimeError("Unable to delete trade")
