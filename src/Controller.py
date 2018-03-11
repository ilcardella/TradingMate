from .Model import Model
from .Utils import Callbacks
from .View import View


class Controller():

    def __init__(self):
        # Init the model
        self.model = Model()
        self.model.set_callback(Callbacks.UPDATE_LIVE_PRICES, self.update_live_price)
        # Init the view
        self.view = View()
        self.view.set_callback(Callbacks.ON_CLOSE_VIEW_EVENT, self.on_close_view_event)

    def start(self):
        self.model.start()
        for logEntry in self.model.get_log_as_list():
            self.view.add_entry_to_log(logEntry.get_date(),
                                        logEntry.get_action(), 
                                        logEntry.get_symbol(),
                                        logEntry.get_amount(),
                                        logEntry.get_price(),
                                        logEntry.get_fee())

        self.view.start() # This should be the last instruction in this function

    def on_close_view_event(self):
        self.model.stop_application()
        self.stop_application()

    def stop_application(self):
        print("TODO Controller stop_application")

    def update_live_price(self, priceDict):
        # priceDict is a simple match of symbols and price
        # Here we calculate the cost, fees and profits before updating the view
        profitLoss = 0
        holdingsData = {}
        for symbol in priceDict.keys():
            amount = self.model.get_holdings()[symbol]
            openPrice = self.model.get_holding_open_price(symbol)
            lastPrice = priceDict[symbol]
            cost = amount * (openPrice / 100) # in [GBP]
            value = amount * (lastPrice / 100) # in [GBP]
            pl = value - cost
            pl_pc = ((value - cost) * 100) / cost
            liveData = {}
            liveData["amount"] = amount
            liveData["open"] = openPrice
            liveData["last"] = lastPrice
            liveData["cost"] = cost
            liveData["value"] = value
            liveData["pl_pc"] = pl_pc
            liveData["pl"] = pl
            holdingsData[symbol] = liveData

            profitLoss += pl
        
        # Calculate current balances (portfolio value)
        freeCash = self.model.get_cash_available()
        holdingValue = 0
        for liveDataDict in holdingsData.values():
            holdingValue += liveDataDict["value"]
        balances = {}
        balances["cash"] = freeCash
        balances["portfolio"] = holdingValue
        balances["total"] = freeCash + holdingValue

        # Update the view
        self.view.update_live_price(holdingsData)
        self.view.update_balances(balances)
        self.view.update_profits(profitLoss)

