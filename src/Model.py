from .TaskThread import TaskThread

import sys
from enum import Enum
import xml.etree.ElementTree as ET
import threading
import time
import sys
import urllib.request
import json

# Enumerations
class Actions(Enum):
    BUY = 1
    SELL = 2
    FUNDING = 3
    DIVIDEND = 4

# Globals
CONFIG_FILE_PATH = "data/config_private.xml"
WEB_POLLING_SECONDS = 15 #Seconds

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

class LivePricesWebThread(TaskThread):

    def __init__(self, model, updatePeriod):
        TaskThread.__init__(self, updatePeriod)
        self.model = model
        self.read_configuration()

    def read_configuration(self):
        try:
            self.configValues = ET.parse(CONFIG_FILE_PATH).getroot()
            self.alphaVantageAPIKey = self.configValues.find("ALPHAVANTAGE_API_KEY").text
            self.alphaVantageBaseURL = self.configValues.find("ALPHAVANTAGE_BASE_URL").text
            # add other config parameters
        except Exception as e:
            print("Model:read_configuration() {0}".format(e))
            sys.exit(1)

    def task(self):
        # Get list of symbols
        # self.model.get_symbols_list()
        # Build the URL
        function = "function=TIME_SERIES_INTRADAY"
        symbol = "symbol=GOOG"
        interval = "interval=1min"
        apiKey = "apikey=" + self.alphaVantageAPIKey
        url = self.alphaVantageBaseURL + function + "&" + symbol + "&" + interval + "&" + apiKey
        # Make HTTP request
        request = urllib.request.urlopen(url)
        data = request.read()
        content = json.loads(data.decode('utf-8'))
        timeSerie = content["Time Series (1min)"]
        last = next(iter(timeSerie.values()))
        value = last["4. close"]
        # Build dictionary
        pricesDict = {'symbol':'GOOG', 
                        'amount':value,
                        'open':1,
                        'last':1,
                        'cost':1,
                        'value':1,
                        'pl':1} # Testing code
        # Save data
        self.model.update_live_prices(pricesDict)

class Model():

    def __init__(self, updateLivePricesCallback):
        self.read_configuration()
        self.update_live_prices = updateLivePricesCallback
        self.livePricesThread = LivePricesWebThread(self, WEB_POLLING_SECONDS)
        self.read_database()

# INTERNAL FUNCTIONS

    def read_configuration(self):
        try:
            self.configValues = ET.parse(CONFIG_FILE_PATH).getroot()
            self.dbFilePath = self.configValues.find("TRADING_LOG_PATH").text
        except Exception as e:
            print("Model.py:121 {0}".format(e))
            sys.exit(1)

    def read_database(self):
        try:
            self.tradingLogXMLTree = ET.parse(self.dbFilePath)
            self.log = self.tradingLogXMLTree.getroot()
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
        self.livePricesThread.shutdown()

    def add_log_entry(self, logEntry):
        self.log.append(logEntry)
        self.tradingLogXMLTree.write(self.dbFilePath)
    
    def remove_log_entry(self, logEntry):
        self.log.remove(logEntry)
        self.tradingLogXMLTree.write(self.dbFilePath)

    
