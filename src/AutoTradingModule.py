import threading
from .TaskThread import TaskThread
from .IG_Interface import IG

class AutoTradingThread(TaskThread):
    def __init__(self, updatePeriod, brokerData):
        TaskThread.__init__(self, updatePeriod)
        self.ig = IG(True, brokerData)
        self.ig.authenticate()

    def task(self):
        print("I am alive!")
        # TODO
        # Fetch price
        # Evaluate buy condition
        # Evaluate sell condition
        # Evaluate exit buy condition
        # Evaluate exit sell condition
        # Check if position is already open
        # Close position if required
        # or
        # Check margin limits
        # Check enough funds
        # Open position

class AutoTradingModule():
    
    def __init__(self, configurationManager):
        self.configurationManager = configurationManager
        brokerData = {
            'broker': self.configurationManager.get_autotrading_broker(),
            'username': self.configurationManager.get_autotrading_username(),
            'password': self.configurationManager.get_autotrading_password(),
            'apiKey': self.configurationManager.get_autotrading_apikey(),
            'accountId': self.configurationManager.get_autotrading_account()
        }
        self.autoTradingThread = AutoTradingThread(5, brokerData)
        self._enabled = False
        self.autoTradingThread.enable(self._enabled) # Disable by default
        self.autoTradingThread.start()
    
    def enable(self, enable):
        self._enabled = enable
        self.autoTradingThread.enable(self._enabled)
    
    def shutdown(self):
        self.autoTradingThread.shutdown()
        self.autoTradingThread.join()

    def get_status(self):
        return self._enabled



