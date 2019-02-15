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

from Utils.Utils import Utils

class ConfigurationManager():
    """
    Class that loads the configuration and credentials json files exposing
    static methods to provide the configurable parameters
    """

    def __init__(self):
        # Load configuration file
        config_filepath = '{}/.TradingMate/config/config.json'.format(str(Path.home()))
        os.makedirs(os.path.dirname(config_filepath), exist_ok=True)
        self.config = Utils.load_json_file(config_filepath)
        if self.config is None:
            logging.error("Please configure TradingMate: {}".format(config_filepath))
            raise RuntimeError("Empty configuration file")

        # Load credentials file
        try:
            credentials_filepath = self.config['general']['credentials_filepath']
            credentials_filepath = credentials_filepath.replace('{home}', str(Path.home()))
        except:
            credentials_filepath = '{}/.TradingMate/config/.credentials'.format(str(Path.home()))
            os.makedirs(os.path.dirname(credentials_filepath), exist_ok=True)
            logging.error("credentials filepath parameter not configured! Using default: {}".format(credentials_filepath))

        credentials_json = Utils.load_json_file(credentials_filepath)
        if credentials_json is None:
            logging.warning('Credentials not configured: {}'.format(credentials_filepath))
            credentials_json = {'av_api_key':''}
        self.credentials = credentials_json
        logging.info('ConfigurationManager initialised')

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

    def get_log_filepath(self):
        """
        Get the log filepath
        """
        return '{home}/.TradingMate/log/trading_mate_{timestamp}.log'
