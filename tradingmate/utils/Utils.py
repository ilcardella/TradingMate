import json
import logging
from pathlib import Path


class Utils:
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
            with open(filepath, "r") as file:
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
            with open(filepath, "w") as file:
                json.dump(data, file, indent=4, separators=(",", ": "))
                return True
        except Exception as e:
            logging.error("Unable to write JSON file: {}".format(e))
        return False

    @staticmethod
    def get_install_path():
        """
        Returns the installation path of TradingMate
        """
        return str(Path.home() / ".TradingMate")
