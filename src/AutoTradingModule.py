import threading
from .TaskThread import TaskThread

class AutoTradingThread(TaskThread):
    def __init__(self, updatePeriod):
        TaskThread.__init__(self, updatePeriod)

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
    
    def __init__(self):
        self._enabled = False
        self.autoTradingThread = AutoTradingThread(5)
        self.autoTradingThread.enable(_enabled) # Disable by default
        self.autoTradingThread.start()
    
    def enable(self, enable):
        self._enabled = enable
        self.autoTradingThread.enable(self._enabled)
    
    def shutdown(self):
        self.autoTradingThread.shutdown()
        self.autoTradingThread.join()

    def get_status(self):
        return self._enabled



