import inspect
import json
import logging
import os
import sys

from Utils.Utils import Utils


class ConfigurationManager:
    """
    Class that loads the configuration and credentials json files exposing
    static methods to provide the configurable parameters
    """

    def __init__(self, config_path):
        self._load_config(config_path)
        self._load_credentials()
        logging.info("ConfigurationManager initialised")

    def _load_config(self, config_path):
        """
        Load the configuration file
        """
        self.config_filepath = config_path
        self.config = Utils.load_json_file(self.config_filepath)
        if self.config is None:
            logging.error(
                "Please configure TradingMate: {}".format(self.config_filepath)
            )
            raise RuntimeError("Empty configuration file")

    def _load_credentials(self):
        """
        Load the credentials file
        """
        try:
            credentials_filepath = self.config["general"]["credentials_filepath"]
        except:
            credentials_filepath = "{}/config/.credentials".format(
                Utils.get_install_path()
            )
            os.makedirs(os.path.dirname(credentials_filepath), exist_ok=True)
            logging.error(
                "credentials filepath parameter not configured! Using default: {}".format(
                    credentials_filepath
                )
            )

        credentials_json = Utils.load_json_file(credentials_filepath)
        if credentials_json is None:
            logging.warning(
                "Credentials not configured: {}".format(credentials_filepath)
            )
            credentials_json = {"av_api_key": "unconfigured"}

        self.config["credentials"] = credentials_json

    def get_trading_database_path(self):
        """
        Get the filepath of the trading log file
        """
        return self.config["trading_logs"]

    def get_credentials_path(self):
        """
        Get the filepath of the credentials file
        """
        return self.config["general"]["credentials_filepath"]

    def get_polling_period(self):
        """
        Get the application polling period
        """
        return float(self.config["general"]["polling_period_sec"])

    def get_configured_stocks_interface(self):
        """
        Get the active configured stock interface
        """
        return self.config["general"]["stocks_interface"]["active"]

    def get_alpha_vantage_api_key(self):
        """
        Get the alphavantage api key
        """
        return self.config["credentials"]["av_api_key"]

    def get_alpha_vantage_base_url(self):
        """
        Get the alphavantage API base URI
        """
        return self.config["alpha_vantage"]["api_base_uri"]

    def get_alpha_vantage_polling_period(self):
        """
        Get the alphavantage configured polling period
        """
        return float(self.config["alpha_vantage"]["polling_period_sec"])

    def get_yfinance_polling_period(self):
        """
        Get the yfinance configured polling period
        """
        return float(self.config["yfinance"]["polling_period_sec"])

    def get_editable_config(self):
        """
        Get a dictionary containing the editable configuration parameters
        """
        return self.config

    def save_settings(self, config):
        """
        Save the edited configuration settings
        """
        # Overwrite settings
        self.config = config
        self._load_credentials()
        # Remove credentials part
        del config["credentials"]
        # Write into file
        Utils.write_json_file(self.config_filepath, config)
        logging.info("ConfigurationManater - settings have been saved")
