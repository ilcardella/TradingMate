import os
import sys
import inspect
import logging
import datetime as dt

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Model.DatabaseHandler import DatabaseHandler
from Utils.Utils import Callbacks
from UI.View import View
from Model.Portfolio import Portfolio
from Utils.ConfigurationManager import ConfigurationManager
from Utils.Utils import Utils


class TradingMate():
    """
    Main class that handles the interaction between the User Interface and the
    underlying business logic of the whole application
    """
    LOG_FILEPATH = '{home}/.TradingMate/log/trading_mate_{timestamp}.log'

    def __init__(self):
        self.setup_logging()
        # Init the configuration manager
        self.configurationManager = ConfigurationManager()
        # Database handler
        self.db_handler = DatabaseHandler(self.configurationManager)
        # Init the portfolio
        self.portfolio = Portfolio("Portfolio1", self.configurationManager)
        # Init the view
        self.view = View()
        # Register callbacks
        self.register_callbacks()
        logging.info('TradingMate initialised')

    def setup_logging(self):
        """
        Setup the global logging settings
        """
        time_str = dt.datetime.now().isoformat()
        time_suffix = time_str.replace(':', '_').replace('.', '_')
        log_filename = self.LOG_FILEPATH.replace(
            '{timestamp}', time_suffix).replace('{home}', Utils.get_home_path())
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        logging.basicConfig(filename=log_filename,
                            level=logging.INFO,
                            format="[%(asctime)s] %(levelname)s: %(message)s")

    def register_callbacks(self):
        """
        Register all the callback functions
        """
        self.portfolio.set_callback(
            Callbacks.UPDATE_LIVE_PRICES, self.on_update_live_price)
        # Init the view
        self.view.set_callback(
            Callbacks.ON_CLOSE_VIEW_EVENT, self.on_close_view_event)
        self.view.set_callback(
            Callbacks.ON_MANUAL_REFRESH_EVENT, self.on_manual_refresh_event)
        self.view.set_callback(
            Callbacks.ON_NEW_TRADE_EVENT, self.on_new_trade_event)
        self.view.set_callback(
            Callbacks.ON_SET_AUTO_REFRESH_EVENT, self.on_set_auto_refresh)
        self.view.set_callback(
            Callbacks.ON_OPEN_LOG_FILE_EVENT, self.on_open_portfolio_event)
        self.view.set_callback(
            Callbacks.ON_SAVE_LOG_FILE_EVENT, self.on_save_portfolio_event)
        self.view.set_callback(
            Callbacks.ON_DELETE_LAST_TRADE_EVENT, self.on_delete_last_trade_event)
        self.view.set_callback(
            Callbacks.ON_SHOW_SETTINGS_EVENT, self.on_show_settings_event)
        self.view.set_callback(
            Callbacks.ON_SAVE_SETTINGS_EVENT, self.on_save_settings_event)
        logging.info('TradingMate - callbacks registered')

    def start(self):
        """
        Start the application
        """
        logging.info('TradingMate start')
        # Read the configured database
        self.db_handler.read_data()
        # Start portfolio
        self.portfolio.start(self.db_handler.get_trades_list())
        # Update the UI
        self._update_share_trading_view(updateHistory=True)
        # This should be the last instruction in this function
        self.view.start()

# Functions

    def _update_share_trading_view(self, updateHistory=False):
        """
        Collect data from the model and update the view
        """
        self.view.reset_view(updateHistory)
        # Update history table if required
        if updateHistory:
            logAsList = self.db_handler.get_trades_list()[
                ::-1]  # Reverse order
            self.view.update_share_trading_history_log(logAsList)
        # get the balances from the portfolio and update the view
        cash = self.portfolio.get_cash_available()
        holdingsValue = self.portfolio.get_holdings_value()
        totalValue = self.portfolio.get_total_value()
        pl = self.portfolio.get_portfolio_pl()
        pl_perc = self.portfolio.get_portfolio_pl_perc()
        holdingPL = self.portfolio.get_open_positions_pl()
        holdingPLPC = self.portfolio.get_open_positions_pl_perc()
        # Update the view
        validity = True
        for h in self.portfolio.get_holding_list():
            self.view.update_share_trading_holding(h.get_symbol(), h.get_quantity(), h.get_open_price(),
                                                   h.get_last_price(), h.get_cost(), h.get_value(), h.get_profit_loss(), h.get_profit_loss_perc(), h.get_last_price_valid())
            validity = validity and h.get_last_price_valid()
        self.view.update_share_trading_portfolio_balances(
            cash, holdingsValue, totalValue, pl, pl_perc, holdingPL, holdingPLPC, validity)

# EVENTS

    def on_close_view_event(self):
        """
        Callback function to handle close event of the user interface
        """
        logging.info('UserInterface main window closed')
        self.portfolio.stop()
        self.db_handler.write_data()
        logging.info('TradingMate stop')

    def on_manual_refresh_event(self):
        """
        Callback function to handle refresh data request
        """
        self.portfolio.on_manual_refresh_live_data()

    def on_set_auto_refresh(self, enabled):
        """
        Callback function to handle set/unset of auto refresh data
        """
        self.portfolio.set_auto_refresh(enabled)

    def on_update_live_price(self):
        """
        Callback function to handle update of stock prices data
        """
        self._update_share_trading_view()

    def on_new_trade_event(self, new_trade):
        """
        Callback function to handle new trade event
        """
        logging.info('TradingMate - new trade event {}'.format(new_trade))
        # Validate trade
        if not self.portfolio.is_trade_valid(new_trade):
            raise RuntimeError('Trade is invalid')
        # Update databse
        self.db_handler.add_trade(new_trade)
        # Reload portfolio
        self.portfolio.reload(self.db_handler.get_trades_list())
        # Update the ui
        self._update_share_trading_view(updateHistory=True)

    def on_delete_last_trade_event(self):
        """
        Callback function to handle delete of last trade request
        """
        logging.info('TradingMate - delete last trade request')
        # Remove trade from database
        self.db_handler.remove_last_trade()
        # Reload portfolio
        self.portfolio.reload(self.db_handler.get_trades_list())
        # Update the UI
        self._update_share_trading_view(updateHistory=True)

    def on_open_portfolio_event(self, filepath):
        """
        Callback function to handle request to open a new portfolio file
        """
        logging.info(
            'TradingMate - open portfolio request from {}'.format(filepath))
        # Read database from filepath
        self.db_handler.read_data(filepath)
        # Reload portfolio
        self.portfolio.reload(self.db_handler.get_trades_list())
        # Update the UI
        self.view.reset_view(resetHistory=True)
        self._update_share_trading_view(updateHistory=True)

    def on_save_portfolio_event(self, filepath):
        """
        Callback function to handle request to save/export the portfolio
        """
        logging.info(
            'TradingMate - save portfolio request to {}'.format(filepath))
        # Write data into the database
        self.db_handler.write_data(filepath=filepath)

    def on_show_settings_event(self):
        """
        Callback to handle request to show the settings panel
        """
        return self.configurationManager.get_editable_config()

    def on_save_settings_event(self, config):
        """
        Callback to save edited settings
        """
        self.configurationManager.save_settings(config)
        self.db_handler.read_data(self.configurationManager.get_trading_database_path())
        self.portfolio.reload(self.db_handler.get_trades_list())
        self._update_share_trading_view(updateHistory=True)
        logging.info('TradingMate - application reloaded')
