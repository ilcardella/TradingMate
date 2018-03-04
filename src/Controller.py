from .Model import Model
from .View import View

import threading
import time
import sys

class WebThread(threading.Thread):

    def __init__(self, name, period):
        threading.Thread.__init__(self)
        self.name = name
        self.period = period # seconds
        self.killThread = False
        self.updateCallback = None
    
    def set_update_callback(self, callback):
        self.updateCallback = callback

    def run(self):
        # While loop where every 30 sec pull data from http API
        lastRequest = time.time()
        while(True):
            if self.killThread:
                break
            now = time.time()
            if(now - lastRequest > self.period):
                try:
                    #TODO pull data from HTTP API
                    pricesDict = {'now':now, 'lastRequest':lastRequest} # Testing code
                except Exception as e:
                    print("Controller.py: {0}".format(e))

                self.updateCallback(pricesDict)
                lastRequest = now

    def kill(self):
        self.killThread = True

class Controller():

    def __init__(self):
        # Init the model
        self.model = Model()

        # Init the view
        self.view = View()
        self.view.set_close_event_callback(self.on_close_view)
        self.view.set_log_list(self.model.get_log_as_list())

        self.webThread = WebThread("WebThread1", 5)
        self.webThread.set_update_callback(self.view.set_stock_prices)

    def start(self):
        self.webThread.start()
        self.view.start() # This should be last instruction in this function

    def on_close_view(self):
        self.webThread.kill() # Send kill command
        self.webThread.join() # Wait for the Thread to end
