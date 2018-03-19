from .Model import Model
from .Utils import Callbacks, Actions
from .View import View


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
        for logEntry in self.model.get_log_as_list():
            self.view.add_entry_to_log_table(logEntry)
        self.view.start() # This should be the last instruction in this function

# Functions

    def _check_new_trade_validity(self, newTrade):
        result = {"success":True,"message":"ok"}

        if newTrade["action"] == Actions.WITHDRAW.name:
            if newTrade["amount"] > self.model.get_cash_available():
                result["success"] = False
                result["message"] = "Error: Insufficient funding available"
        elif newTrade["action"] == Actions.BUY.name:
            cost = (newTrade["price"] * newTrade["amount"]) / 100 # in £
            fee = newTrade["fee"]
            tax = (newTrade["stamp_duty"] * cost) / 100
            totalCost = cost + fee + tax
            if totalCost > self.model.get_cash_available():
                result["success"] = False
                result["message"] = "Error: Insufficient funding available"
        elif newTrade["action"] == Actions.SELL.name:
            if newTrade["symbol"] not in self.model.get_holdings() \
                or newTrade["amount"] > self.model.get_holdings()[newTrade["symbol"]]:
                result["success"] = False
                result["message"] = "Error: Insufficient holding available"

        return result

# EVENTS

    def on_close_view_event(self):
        self.model.stop_application()

    def on_manual_refresh_event(self):
        self.model.on_manual_refresh_live_data()

    def on_set_auto_refresh(self, enabled):
        self.model.set_auto_refresh(enabled)

    def on_update_live_price(self, priceDict):
        # priceDict is a dict {symbol: price}
        # Here we calculate the cost, fees and profits before updating the view
        holdingValue = 0
        holdingsData = {}
        for symbol in priceDict.keys():
            amount = self.model.get_holdings()[symbol]
            openPrice = self.model.get_holding_open_price(symbol)
            lastPrice = priceDict[symbol]
            cost = amount * (openPrice / 100) # in [£]
            value = amount * (lastPrice / 100) # in [£]
            pl = value - cost
            pl_pc = (pl * 100) / cost
            liveData = {}
            liveData["amount"] = amount
            liveData["open"] = openPrice
            liveData["last"] = lastPrice
            liveData["cost"] = cost
            liveData["value"] = value
            liveData["pl_pc"] = pl_pc
            liveData["pl"] = pl
            holdingsData[symbol] = liveData

            holdingValue += value
        
        # Calculate current balances (portfolio value)
        freeCash = self.model.get_cash_available()
        investedAmount = self.model.get_invested_amount()
        balances = {}
        balances["cash"] = freeCash
        balances["portfolio"] = holdingValue
        balances["total"] = freeCash + holdingValue
        balances["pl"] = balances["total"] - investedAmount
        if not investedAmount == 0:
            balances["pl_pc"] = (balances["pl"] * 100) / investedAmount
        else:
            balances["pl_pc"] = 0

        # Update the view
        self.view.update_live_price(holdingsData)
        self.view.update_balances(balances)

    def on_new_trade_event(self, newTrade):
        result = {"success":True,"message":"ok"}

        valResult = self._check_new_trade_validity(newTrade)

        if valResult["success"]:
            modelResult = self.model.add_new_trade(newTrade) # Update the model
            if modelResult["success"]:
                self.view.add_entry_to_log_table(newTrade) # Update the view
                self.view.refresh_live_data()
            else:
                return modelResult
        else:
            return valResult
        return result

    def on_open_log_file_event(self, filepath):
        result = self.model.open_log_file(filepath)
        if result["success"]:
            self.view.reset_view()
            for logEntry in self.model.get_log_as_list():
                self.view.add_entry_to_log_table(logEntry)
            self.on_manual_refresh_event()
        return result

    def on_save_log_file_event(self, filepath):
        return self.model.save_log_file(filepath)
