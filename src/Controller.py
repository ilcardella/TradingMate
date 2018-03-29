from .Model import Model
from .Utils import Callbacks, Actions, Messages
from .View import View
from .Portfolio import Portfolio


class Controller():

    def __init__(self):
        # Init the model
        self.model = Model()
        self.model.set_callback(Callbacks.UPDATE_LIVE_PRICES, self.on_update_live_price)
        # Init the view
        self.view = View()
        self.view.set_callback(Callbacks.ON_CLOSE_VIEW_EVENT, self.on_close_view_event)
        self.view.set_callback(Callbacks.ON_MANUAL_REFRESH_EVENT, self.on_manual_refresh_event)
        self.view.set_callback(Callbacks.ON_NEW_TRADE_EVENT, self.on_new_trade_event)
        self.view.set_callback(Callbacks.ON_SET_AUTO_REFRESH_EVENT, self.on_set_auto_refresh)
        self.view.set_callback(Callbacks.ON_OPEN_LOG_FILE_EVENT, self.on_open_log_file_event)
        self.view.set_callback(Callbacks.ON_SAVE_LOG_FILE_EVENT, self.on_save_log_file_event)

    def start(self):
        self.model.start()
        self._update_share_trading_view(updateHistory=True)
        
        self.view.start() # This should be the last instruction in this function

# Functions

    def _check_new_trade_validity(self, newTrade):
        result = {"success":True,"message":"ok"}
        portfolio = self.model.get_portfolio()

        if newTrade["action"] == Actions.WITHDRAW.name:
            if newTrade["amount"] > portfolio.get_cash_available():
                result["success"] = False
                result["message"] = Messages.INSUF_FUNDING.value
        elif newTrade["action"] == Actions.BUY.name:
            cost = (newTrade["price"] * newTrade["amount"]) / 100 # in £
            fee = newTrade["fee"]
            tax = (newTrade["stamp_duty"] * cost) / 100
            totalCost = cost + fee + tax
            if totalCost > portfolio.get_cash_available():
                result["success"] = False
                result["message"] = Messages.INSUF_FUNDING.value
        elif newTrade["action"] == Actions.SELL.name:
            if portfolio.get_holding_amount(newTrade["symbol"]) > 0 \
                or newTrade["amount"] > portfolio.get_holding_amount(newTrade["symbol"]):
                result["success"] = False
                result["message"] = Messages.INSUF_HOLDINGS.value

        return result
    
    def _update_share_trading_view(self, updateHistory=False):
        # Update the database filepath shown in the share trading frame
        filepath = self.model.get_db_filepath()
        self.view.set_db_filepath(filepath)
        # Update history table if required
        if updateHistory:
            logAsList = self.model.get_log_as_list()[::-1] # Reverse order
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
        self.view.reset_view()
        for h in portfolio.get_holding_list():
            self.view.update_share_trading_holding(h.get_symbol(), h.get_amount(), h.get_open_price(),\
             h.get_last_price(), h.get_cost(), h.get_value(), h.get_profit_loss(), h.get_profit_loss_perc())
        self.view.update_share_trading_portfolio_balances(cash, holdingsValue, totalValue, pl, pl_perc, holdingPL, holdingPLPC)

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
        result = {"success":True,"message":"ok"}

        valResult = self._check_new_trade_validity(newTrade)

        if valResult["success"]:
            modelResult = self.model.add_new_trade(newTrade) # Update the model
            if modelResult["success"]:
                #self.view.add_entry_to_log_table(newTrade) # Update the view
                self._update_share_trading_view()
                #self.view.refresh_live_data()
            else:
                return modelResult
        else:
            return valResult
        return result

    def on_open_log_file_event(self, filepath):
        result = self.model.open_log_file(filepath)
        if result["success"]:
            self.view.reset_view()
            self._update_share_trading_view()
            #self.view.refresh_live_data()
        return result

    def on_save_log_file_event(self, filepath):
        return self.model.save_log_file(filepath)
