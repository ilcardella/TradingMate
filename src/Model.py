import sys
from enum import Enum
import xml.etree.ElementTree as ET
import threading
import time
import sys

# Enumerations
class Actions(Enum):
    BUY = 1
    SELL = 2
    FUNDING = 3
    DIVIDEND = 4

# Globals
DB_FILE_PATH = "data/trading_log.xml"
WEB_POLLING_SECONDS = 5 #Seconds

#Class definitions
class StockLogEntry():

    def __init__(self, date, action, symbol, amount, fee, price):
        self.date = date
        self.action = action
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.fee = fee

    def get_date(self):
        return self.date
    def get_action(self):
        return self.action
    def get_symbol(self):
        return self.symbol
    def get_amount(self):
        return self.amount
    def get_price(self):
        return self.price
    def get_fee(self):
        return self.fee

    def __str__(self):
        return str(self.date)+","+str(self.action)+","+str(self.symbol)+","+str(self.amount)+","+str(self.price)+","+str(self.fee)

class WebThread(threading.Thread):

    def __init__(self, name, updateCallback, updatePeriod):
        threading.Thread.__init__(self)
        self.name = name
        self.updatePeriod = updatePeriod # seconds
        self.killThread = False
        self.updateCallback = updateCallback

    def run(self):
        lastRequest = time.time()
        while(True):
            if self.killThread:
                break
            now = time.time()
            if(now - lastRequest > self.updatePeriod):
                try:
                    #TODO pull data from HTTP API
                    pricesDict = {'symbol':'GOOG', 
                                    'amount':lastRequest,
                                    'open':1,
                                    'last':1,
                                    'cost':1,
                                    'value':1,
                                    'pl':1} # Testing code
                except Exception as e:
                    print("Controller.py: {0}".format(e))

                self.updateCallback(pricesDict)
                lastRequest = now

    def kill(self):
        self.killThread = True

class Model():

    def __init__(self, updateLivePricesCallback):
        self.update_live_prices = updateLivePricesCallback
        self.read_configuration()
        self.read_database()
        self.livePricesThread = WebThread("livePricesThread", self.update_live_prices, WEB_POLLING_SECONDS)

# INTERNAL FUNCTIONS

    def read_configuration(self):
        # Read from xml config file
        self.dbFilename = DB_FILE_PATH

    def read_database(self):
        try:
            self.xmlTree = ET.parse(self.dbFilename)
            self.log = self.xmlTree.getroot()
        except Exception as e:
            print("Model.py: {0}".format(e))
            sys.exit(1)

# GETTERS

    def get_log_as_list(self):
        # Alternative is to return a list of Dict instead of using a class
        return [StockLogEntry(row.find('date').text,
                                row.find('action').text,
                                row.find('symbol').text,
                                row.find('amount').text,
                                row.find('fee').text,
                                row.find('price').text) for row in self.log]
    
# INTERFACES

    def start(self):
        self.livePricesThread.start()

    def stop_application(self):
        self.livePricesThread.kill() # Send kill command
        self.livePricesThread.join() # Wait for the Thread to end

    def add_log_entry(self, logEntry):
        self.log.append(logEntry)
        self.xmlTree.write(self.dbFilename)
    
    def remove_log_entry(self, logEntry):
        self.log.remove(logEntry)
        self.xmlTree.write(self.dbFilename)

    
