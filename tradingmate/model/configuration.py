import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..utils import Utils

# FIXME Property should be of type JSON byt it requires typing to accepts recursive types
Property = Any
ConfigDict = Dict[str, Property]
CredentialDict = Dict[str, str]

DEFAULT_CREDENTIALS_PATH: Path = Path(
    Utils.get_install_path(), "config", ".credentials"
)


class ConfigurationManager:
    """
    Class that loads the configuration and credentials files exposing
    methods to provide the configurable parameters
    """

    config_filepath: Path
    config: ConfigDict
    credentials: CredentialDict

    def __init__(self, config_path: Path) -> None:
        self.config_filepath = config_path
        self.config = self._load_config()
        self.credentials = self._load_credentials()
        logging.info("ConfigurationManager initialised")

    def _load_config(self) -> ConfigDict:
        """
        Load the configuration file
        """
        with self.config_filepath.open(mode="r") as file:
            config = self._parse_raw_config(json.load(file))
            return config

    def _load_credentials(self) -> CredentialDict:
        """
        Load the credentials file
        """
        if Path(self.get_credentials_path()).exists():
            with Path(self.get_credentials_path()).open(mode="r") as f:
                return json.load(f)
        else:
            logging.warning(
                "Credentials not found: {}".format(str(self.get_credentials_path()))
            )
            if DEFAULT_CREDENTIALS_PATH.exists():
                with DEFAULT_CREDENTIALS_PATH.open(mode="r") as f:
                    return json.load(f)
            else:
                logging.warning("Credentials not configured")
        return {"av_api_key": "unconfigured"}

    def _parse_raw_config(self, config_dict: ConfigDict) -> ConfigDict:
        config_copy = config_dict
        for key, value in config_copy.items():
            if type(value) is dict:
                config_dict[key] = self._parse_raw_config(value)
            elif type(value) is list:
                for i in range(len(value)):
                    config_dict[key][i] = (
                        self._replace_placeholders(config_dict[key][i])
                        if type(config_dict[key][i]) is str
                        else config_dict[key][i]
                    )
            elif type(value) is str:
                config_dict[key] = self._replace_placeholders(config_dict[key])
        return config_dict

    def _replace_placeholders(self, string: str) -> str:
        string = string.replace("{home}", str(Path.home()))
        string = string.replace(
            "{timestamp}",
            datetime.now().isoformat().replace(":", "_").replace(".", "_"),
        )
        return string

    def get_log_filepath(self) -> Path:
        """
        Get the filepath of the log file
        """
        filename = self._replace_placeholders("trading_mate_{timestamp}.log")
        return Path(Utils.get_install_path(), "log", filename)

    def get_trading_database_path(self) -> List[Path]:
        """
        Get the filepath of the trading log file
        """
        return [Path(p) for p in self.config["trading_logs"]]

    def get_credentials_path(self) -> Path:
        """
        Get the filepath of the credentials file
        """
        return Path(self.config["general"]["credentials_filepath"])

    def get_polling_period(self) -> float:
        """
        Get the application polling period
        """
        return float(self.config["general"]["polling_period_sec"])

    def get_configured_stocks_interface(self) -> str:
        """
        Get the active configured stock interface
        """
        return self.config["general"]["stocks_interface"]["active"]

    def get_alpha_vantage_api_key(self) -> str:
        """
        Get the alphavantage api key
        """
        return self.credentials["av_api_key"]

    def get_alpha_vantage_base_url(self) -> str:
        """
        Get the alphavantage API base URI
        """
        return self.config["alpha_vantage"]["api_base_uri"]

    def get_alpha_vantage_polling_period(self) -> float:
        """
        Get the alphavantage configured polling period
        """
        return float(self.config["alpha_vantage"]["polling_period_sec"])

    def get_yfinance_polling_period(self) -> float:
        """
        Get the yfinance configured polling period
        """
        return float(self.config["yfinance"]["polling_period_sec"])

    def get_editable_config(self) -> ConfigDict:
        """
        Get a dictionary containing the editable configuration parameters
        """
        return self.config

    def save_settings(self, config: ConfigDict) -> bool:
        """
        Save the edited configuration settings
        """
        # Overwrite settings and reload
        self.config = self._parse_raw_config(config)
        self.credentials = self._load_credentials()
        # Write into file the non-parsed config
        Utils.write_json_file(self.config_filepath, config)
        logging.info("ConfigurationManater - settings have been saved")

        return True
