import threading
from .TaskThread import TaskThread
from .IG_Interface import IG
from enum import Enum
from .Utils import AutoTradeActions

class AutoTradingThread(TaskThread):
    def __init__(self, updatePeriod, brokerData):
        TaskThread.__init__(self, updatePeriod)
        self.epic = 'KA.D.IQE.DAILY.IP' # TODO this should be a list
        self.broker = IG(True, brokerData)
        self.initialised = False

    def task(self):
        if not self.initialised:
            self.broker.authenticate()
            self.initialised = True
        print("I am alive!")
        if self.broker.can_trade():
            # Get price history
            history = self.broker.get_price_history(self.epic, 5)
            # Get current market prices
            prices = self.broker.get_market_prices(self.epic)
            # Evaluate market direction
            marketAction = self.evaluate_market_action(prices, history)
            if marketAction != AutoTradeActions.NONE:
                # Perform trade
                self.broker.trade(marketAction, self.epic)

        # Update the UI with new data
        self.update_UI()

    def evaluate_market_action(self, prices, history):
        # Evaluate what to do: buy, sell, etc.
        # TODO
        print("MArket evaluated: action NONE selected")
        return AutoTradeActions.NONE

    def update_UI(self):
        print("UI Updated")
        pass # TODO call a callback sending all values to update the UI

class AutoTradingModule():
    
    def __init__(self, configurationManager):
        self.configurationManager = configurationManager
        self.callbacks = {}
        brokerData = {
            'broker': self.configurationManager.get_autotrading_broker(),
            'username': self.configurationManager.get_autotrading_username(),
            'password': self.configurationManager.get_autotrading_password(),
            'apiKey': self.configurationManager.get_autotrading_apikey(),
            'accountId': self.configurationManager.get_autotrading_account()
        }
        self._enabled = False
        self.autoTradingThread = AutoTradingThread(5, brokerData)
        self.autoTradingThread.enable(self._enabled)
        self.autoTradingThread.start()
    
    def enable(self, enable):
        self._enabled = enable
        self.autoTradingThread.enable(self._enabled)
    
    def shutdown(self):
        self.autoTradingThread.shutdown()
        self.autoTradingThread.join()

    def get_status(self):
        return self._enabled



