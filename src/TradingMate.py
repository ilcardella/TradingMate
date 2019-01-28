import os
import sys
import inspect
import logging
import datetime as dt

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.ConfigurationManager import ConfigurationManager
from Model.Portfolio import Portfolio
from UI.View import View
from Utils.Utils import Callbacks, Actions, Messages
from Model.Model import Model


class TradingMate():

    def __init__(self):
        # Init the configuration manager
        self.configurationManager = ConfigurationManager()
        # Setup the logging
        self.setup_logging()
        # Init the model
        self.model = Model(self.configurationManager)
        self.model.set_callback(
            Callbacks.UPDATE_LIVE_PRICES, self.on_update_live_price)
        # Init the view
        self.view = View()
        self.view.set_callback(
            Callbacks.ON_CLOSE_VIEW_EVENT, self.on_close_view_event)
        self.view.set_callback(
            Callbacks.ON_MANUAL_REFRESH_EVENT, self.on_manual_refresh_event)
        self.view.set_callback(
            Callbacks.ON_NEW_TRADE_EVENT, self.on_new_trade_event)
        self.view.set_callback(
            Callbacks.ON_SET_AUTO_REFRESH_EVENT, self.on_set_auto_refresh)
        self.view.set_callback(
            Callbacks.ON_OPEN_LOG_FILE_EVENT, self.on_open_log_file_event)
        self.view.set_callback(
            Callbacks.ON_SAVE_LOG_FILE_EVENT, self.on_save_log_file_event)
        self.view.set_callback(
            Callbacks.ON_DELETE_LAST_TRADE_EVENT, self.on_delete_last_trade_event)

    def setup_logging(self):
        """
        Setup the global logging settings
        """
        # Define the global logging settings
        debugLevel = logging.DEBUG if self.configurationManager.get_debug_log_active() else logging.INFO
        # If enabled define log file filename with current timestamp
        if self.configurationManager.get_enable_file_log():
            log_filename = self.configurationManager.get_log_filepath()
            time_str = dt.datetime.now().isoformat()
            time_suffix = time_str.replace(':', '_').replace('.', '_')
            home = str(Path.home())
            log_filename = log_filename.replace(
                '{timestamp}', time_suffix).replace('{home}', home)
            os.makedirs(os.path.dirname(log_filename), exist_ok=True)
            logging.basicConfig(filename=log_filename,
                                level=debugLevel,
                                format="[%(asctime)s] %(levelname)s: %(message)s")
        else:
            logging.basicConfig(level=debugLevel,
                                format="[%(asctime)s] %(levelname)s: %(message)s")

    def start(self):
        self.model.start()
        self._update_share_trading_view(updateHistory=True)
        self.view.start()  # This should be the last instruction in this function

# Functions

    def _check_new_trade_validity(self, newTrade):
        result = {"success": True, "message": "ok"}
        portfolio = self.model.get_portfolio()

        if newTrade["action"] == Actions.WITHDRAW.name:
            if newTrade["amount"] > portfolio.get_cash_available():
                result["success"] = False
                result["message"] = Messages.INSUF_FUNDING.value
        elif newTrade["action"] == Actions.BUY.name:
            cost = (newTrade["price"] * newTrade["amount"]) / 100  # in £
            fee = newTrade["fee"]
            tax = (newTrade["stamp_duty"] * cost) / 100
            totalCost = cost + fee + tax
            if totalCost > portfolio.get_cash_available():
                result["success"] = False
                result["message"] = Messages.INSUF_FUNDING.value
        elif newTrade["action"] == Actions.SELL.name:
            if newTrade["amount"] > portfolio.get_holding_amount(newTrade["symbol"]):
                result["success"] = False
                result["message"] = Messages.INSUF_HOLDINGS.value

        return result

    def _update_share_trading_view(self, updateHistory=False):
        self.view.reset_view(updateHistory)
        # Update the database filepath shown in the share trading frame
        filepath = self.model.get_db_filepath()
        self.view.set_db_filepath(filepath)
        # Update history table if required
        if updateHistory:
            logAsList = self.model.get_log_as_list()[::-1]  # Reverse order
            self.view.update_share_trading_history_log(logAsList)
        # Compute the current holding profits and balances
        portfolio = self.model.get_portfolio()
        # get the balances from the portfolio and update the view
        cash = portfolio.get_cash_available()
        holdingsValue = portfolio.get_holdings_value()
        totalValue = portfolio.get_total_value()
        pl = portfolio.get_portfolio_pl()
        pl_perc = portfolio.get_portfolio_pl_perc()
        holdingPL = portfolio.get_open_positions_pl()
        holdingPLPC = portfolio.get_open_positions_pl_perc()
        # Update the view
        validity = True
        for h in portfolio.get_holding_list():
            self.view.update_share_trading_holding(h.get_symbol(), h.get_amount(), h.get_open_price(),
                                                   h.get_last_price(), h.get_cost(), h.get_value(), h.get_profit_loss(), h.get_profit_loss_perc(), h.get_last_price_valid())
            validity = validity and h.get_last_price_valid()
        self.view.update_share_trading_portfolio_balances(
            cash, holdingsValue, totalValue, pl, pl_perc, holdingPL, holdingPLPC, validity)

# EVENTS

    def on_close_view_event(self):
        self.model.stop_application()

    def on_manual_refresh_event(self):
        self.model.on_manual_refresh_live_data()

    def on_set_auto_refresh(self, enabled):
        self.model.set_auto_refresh(enabled)

    def on_update_live_price(self):
        self._update_share_trading_view()

    def on_new_trade_event(self, newTrade):
        result = {"success": True, "message": "ok"}

        valResult = self._check_new_trade_validity(newTrade)

        if valResult["success"]:
            modelResult = self.model.add_new_trade(
                newTrade)  # Update the model
            if modelResult["success"]:
                self._update_share_trading_view(updateHistory=True)
            else:
                return modelResult
        else:
            return valResult
        return result

    def on_open_log_file_event(self, filepath):
        result = self.model.open_log_file(filepath)
        if result["success"]:
            self.view.reset_view(resetHistory=True)
            self._update_share_trading_view(updateHistory=True)
        return result

    def on_save_log_file_event(self, filepath):
        return self.model.save_log_file(filepath)

    def on_delete_last_trade_event(self):
        result = {"success": True, "message": "ok"}
        result = self.model.delete_last_trade()
        if result["success"]:
            self._update_share_trading_view(updateHistory=True)
        else:
            return result
