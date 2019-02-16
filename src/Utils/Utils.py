from enum import Enum
import os
import sys
import inspect
import json
import logging
from pathlib import Path

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Enumerations

class Callbacks(Enum):
    UPDATE_LIVE_PRICES = 1
    ON_CLOSE_VIEW_EVENT = 2
    ON_MANUAL_REFRESH_EVENT = 3
    ON_NEW_TRADE_EVENT = 4
    ON_SET_AUTO_REFRESH_EVENT = 5
    ON_OPEN_LOG_FILE_EVENT = 6
    ON_SAVE_LOG_FILE_EVENT = 7
    ON_DELETE_LAST_TRADE_EVENT = 8
    ON_START_AUTOTRADING = 9
    ON_STOP_AUTOTRADING = 10

class Actions(Enum):
    BUY = 1
    SELL = 2
    DEPOSIT = 3
    DIVIDEND = 4
    WITHDRAW = 5

class Messages(Enum):
    INSUF_FUNDING = "ERROR: Insufficient funding available"
    INSUF_HOLDINGS = "ERROR: Insufficient holdings available"
    INVALID_OPERATION = "ERROR: Invalid operation"
    ABOUT_MESSAGE = "Creator: Alberto Cardellini\nEmail: albe.carde@gmail.com"
    ERROR_SAVE_FILE = "Error saving the log. Try again."
    ERROR_OPEN_FILE = "Error opening the file. Try again."

class Markets(Enum):
    LSE = "LON"

class Utils():
    """
    Class that provides utility functions
    """
    def __init__(self):
        pass

    @staticmethod
    def load_json_file(filepath):
        """
        Load a JSON formatted file from the given filepath

            - **filepath** The filepath including filename and extension
            - Return a dictionary of the loaded json
        """
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error("Unable to load JSON file {}".format(e))
        return None

    @staticmethod
    def write_json_file(filepath, data):
        """
        Write a python dict object into a file with json formatting

            -**filepath** The filepath
            -**data** The python dict to write
            - Return True if succed, False otherwise
        """
        try:
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4, separators=(',', ': '))
                return True
        except Exception as e:
            logging.error("Unable to write JSON file: ".format(e))
        return False

    @staticmethod
    def get_home_path():
        """
        Returns the user home folder path as string
        """
        if sys.version_info < (3,5):
            return str(os.path.expanduser("~"))
        return str(Path.home())
