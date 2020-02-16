import os
import sys
import inspect
import logging
import datetime as dt
import subprocess
import re

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Model.DatabaseHandler import DatabaseHandler
from Model.Portfolio import Portfolio
from Utils.ConfigurationManager import ConfigurationManager
from Utils.Utils import Utils


class TradingMate:
    """
    Main class that handles the interaction between the User Interface and the
    underlying business logic of the whole application
    """

    LOG_FILEPATH = os.path.join(
        Utils.get_install_path(), "log", "trading_mate_{timestamp}.log"
    )
    CONFIG_FILEPATH = os.path.join(Utils.get_install_path(), "config", "config.json")

    def __init__(self):
        self._setup_logging()
        # Read TradingMate configuration
        self.configurationManager = ConfigurationManager(self.CONFIG_FILEPATH)
        # Create the portfolios
        self._create_portfolios()
        logging.info("TradingMate initialised")

    def _setup_logging(self):
        """
        Setup the global logging settings
        """
        time_str = dt.datetime.now().isoformat()
        time_suffix = time_str.replace(":", "_").replace(".", "_")
        self._app_log_filepath = self.LOG_FILEPATH.replace("{timestamp}", time_suffix)
        os.makedirs(os.path.dirname(self._app_log_filepath), exist_ok=True)
        logging.basicConfig(
            filename=self._app_log_filepath,
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s: %(message)s",
        )

    def _create_portfolios(self):
        """Create the portfolios from the configured trading logs"""
        self.portfolios = []
        for log_path in self.configurationManager.get_trading_database_path():
            self.portfolios.append(Portfolio(self.configurationManager, log_path))

    # Public API

    def get_portfolios(self):
        """Return the list of active portfolios"""
        return self.portfolios

    def close_view_event(self):
        """
        Callback function to handle close event of the user interface
        """
        for pf in self.portfolios:
            pf.stop()
        logging.info("TradingMate stop")

    def manual_refresh_event(self, portfolio_id):
        """
        Callback function to handle refresh data request
        """
        for pf in self.portfolios:
            if pf.get_id() == portfolio_id:
                pf.on_manual_refresh_live_data()

    def set_auto_refresh(self, enabled, portfolio_id):
        """
        Callback function to handle set/unset of auto refresh data
        """
        for pf in self.portfolios:
            if pf.get_id() == portfolio_id:
                pf.set_auto_refresh(enabled)

    def new_trade_event(self, new_trade, portfolio_id):
        """
        Callback function to handle new trade event
        """
        logging.info(
            f"TradingMate - new trade {new_trade.to_string()} for portfolio {portfolio_id}"
        )
        for pf in self.portfolios:
            if pf.get_id() == portfolio_id:
                pf.add_trade(new_trade)

    def delete_last_trade_event(self, portfolio_id):
        """
        Callback function to handle delete of last trade request
        """
        logging.info(
            "TradingMate - delete last trade for portfolio {}".format(portfolio_id)
        )
        for pf in self.portfolios:
            if pf.get_id() == portfolio_id:
                pf.remove_last_trade()

    def open_portfolio_event(self, filepath):
        """
        Callback function to handle request to open a new portfolio file
        """
        logging.info("TradingMate - open portfolio: {}".format(filepath))
        # Create a new Portfolio from the filepath
        pf = Portfolio(self.configurationManager, filepath)
        self.portfolios.append(pf)

    def save_portfolio_event(self, portfolio_id, filepath):
        """
        Callback function to handle request to save/export the portfolio
        """
        logging.info(
            "TradingMate - save portfolio {} to {}".format(portfolio_id, filepath)
        )
        for pf in self.portfolios:
            if pf.get_id() == portfolio_id:
                pf.save_portfolio(filepath)

    def get_settings_event(self):
        """
        Callback to handle request to show the settings panel
        """
        return self.configurationManager.get_editable_config()

    def save_settings_event(self, config):
        """
        Callback to save edited settings
        """
        self.configurationManager.save_settings(config)
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


def main():
    # Initialise the business logic
    tm = TradingMate()
    # Initialise the user interface
    from UI.gtk.UIHandler import UIHandler
    UIHandler(tm).start()


if __name__ == "__main__":
    main()
