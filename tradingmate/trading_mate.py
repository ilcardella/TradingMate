import logging
import re
import subprocess
from pathlib import Path
from typing import List

from .model import ConfigurationManager, Portfolio, Trade
from .model.broker import StocksInterfaceFactory
from .utils import Messages, Utils

DEFAULT_CONFIG_FILEPATH: Path = Path(Utils.get_install_path(), "config", "config.json")


class TradingMate:
    """
    Main class that handles the interaction between the User Interface and the
    underlying business logic of the application
    """

    _config: ConfigurationManager
    _app_log_filepath: Path
    _portfolios: List[Portfolio]

    def __init__(
        self, config_filepath: Path = DEFAULT_CONFIG_FILEPATH,
    ):
        # Read TradingMate configuration
        self._config = ConfigurationManager(config_filepath)
        self._setup_logging()
        # Create the portfolios
        self._portfolios = self._create_portfolios()
        logging.info("TradingMate initialised")

    def _setup_logging(self):
        """
        Setup the global logging settings
        """
        # Clean logging handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        self._app_log_filepath = Path(self._config.get_log_filepath())
        self._app_log_filepath.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=str(self._app_log_filepath),
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s: %(message)s",
        )

    def _create_portfolios(self) -> List[Portfolio]:
        """Create the portfolios from the configured trading logs"""
        return [
            Portfolio(self._config, Path(path))
            for path in self._config.get_trading_database_path()
        ]

    # Public API

    def get_portfolios(self) -> List[Portfolio]:
        """Return the list of active portfolios"""
        return self._portfolios

    def close_view_event(self) -> None:
        """
        Callback function to handle close event of the user interface
        """
        for pf in self._portfolios:
            pf.stop()
        logging.info("TradingMate stop")

    def manual_refresh_event(self, portfolio_id: str) -> None:
        """
        Callback function to handle refresh data request
        """
        for pf in self._portfolios:
            if pf.get_id() == portfolio_id:
                pf.on_manual_refresh_live_data()

    def set_auto_refresh(self, enabled: bool, portfolio_id: str) -> None:
        """
        Callback function to handle set/unset of auto refresh data
        """
        for pf in self._portfolios:
            if pf.get_id() == portfolio_id:
                pf.set_auto_refresh(enabled)

    def new_trade_event(self, new_trade: Trade, portfolio_id: str) -> None:
        """
        Callback function to handle new trade event
        """
        logging.info(
            f"TradingMate - new trade {new_trade.to_string()} for portfolio {portfolio_id}"
        )
        for pf in self._portfolios:
            if pf.get_id() == portfolio_id:
                pf.add_trade(new_trade)

    def delete_trade_event(self, portfolio_id: str, trade_id: str) -> None:
        """
        Callback function to handle delete of a trade
        """
        logging.info(
            "TradingMate - delete trade {} for portfolio {}".format(
                trade_id, portfolio_id
            )
        )
        for pf in self._portfolios:
            if pf.get_id() == portfolio_id:
                pf.delete_trade(trade_id)

    def open_portfolio_event(self, filepath: Path) -> None:
        """
        Callback function to handle request to open a new portfolio file
        """
        logging.info("TradingMate - open portfolio: {}".format(filepath))
        # Create a new Portfolio from the filepath
        pf = Portfolio(self._config, filepath)
        self._portfolios.append(pf)

    def save_portfolio_event(self, portfolio_id: str, filepath: Path) -> None:
        """
        Callback function to handle request to save/export the portfolio
        """
        logging.info(
            "TradingMate - save portfolio {} to {}".format(portfolio_id, filepath)
        )
        for pf in self._portfolios:
            if pf.get_id() == portfolio_id:
                pf.save_portfolio(filepath)

    def get_settings_event(self):
        """
        Callback to handle request to show the settings panel
        """
        return self._config.get_editable_config()

    def save_settings_event(self, config):
        """
        Callback to save edited settings
        """
        self._config.save_settings(config)
        self._create_portfolios()
        logging.info("TradingMate - portfolios reloaded after settings update")

    def get_app_log_filepath(self):
        """Return the full filepath of the log file of application current session"""
        return self._app_log_filepath

    def get_app_version(self):
        # Find the app version with pip
        output = subprocess.Popen(
            "pip3 show TradingMate".split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        # Extract the version from the command output
        match = re.search(
            r"Version:\s([0-9].[0-9].[0-9])", str(output.communicate()[0])
        )
        if match is None:
            return "Unknown"
        return match.group(1).strip()

    def get_market_details(self, market_ticker):
        # Currently only yfinance support this feature
        if "yfinance" not in self._config.get_configured_stocks_interface():
            raise RuntimeError(Messages.UNSUPPORTED_BROKER_FEATURE.value)
        inteface = StocksInterfaceFactory(self._config).make_from_configuration()
        try:
            return inteface.get_market_details(market_ticker)
        except Exception as e:
            logging.error(f"TradingMate get_market_details - {e}")
            raise RuntimeError(Messages.SOMETHING_WRONG.value)
