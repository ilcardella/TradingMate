import os
import sys
import inspect
import json
import logging

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Utils

class ConfigurationManager():
    """
    Class that loads the configuration and credentials json files exposing
    static methods to provide the configurable parameters
    """
    CONFIG_FILEPATH = '../config/config.json'

    def __init__(self):
        # Load configuration file
        self.config = Utils.load_json_file(self.CONFIG_FILEPATH)
        # Load credentials file
        self.credentials = Utils.load_json_file(self.config['general']['credentials_filepath'])

    def get_trading_database_path(self):
        """
        Get the filepath of the trading log file
        """
        return self.config['general']['trading_log_path']

    def get_alpha_vantage_api_key(self):
        """
        Get the alphavantage api key
        """
        return self.credentials['av_api_key']

    def get_alpha_vantage_base_url(self):
        """
        Get the alphavantage API base URI
        """
        return self.config['alpha_vantage']['api_base_uri']

    def get_alpha_vantage_polling_period(self):
        """
        Get the alphavantage configured polling period
        """
        return self.config['alpha_vantage']['polling_period_sec']

    def get_debug_log_active(self):
        """
        Get the logging level
        """
        return self.config['general']['debug_log']

    def get_enable_file_log(self):
        """
        Enable logging on file status
        """
        return self.config['general']['enable_file_log']

    def get_log_filepath(self):
        """
        Get the log filepath
        """
        return self.config['general']['log_filepath']
