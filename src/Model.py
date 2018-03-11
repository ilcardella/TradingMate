from .TaskThread import TaskThread
from .Utils import Callbacks

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
    WITHDRAW = 5

# Globals
CONFIG_FILE_PATH = "data/config_private.xml" # Change this to data/config.xml
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
        priceDict = {}
        for symbol in self.model.get_holdings().keys():
            priceDict[symbol] = self.fetch_price_data(symbol)
        if not self._finished.isSet():
            self.model.update_live_price(priceDict)

    def build_url(self, aLength, aSymbol, anInterval, anApiKey):
        function = "function=" + aLength
        symbol = "symbol=" + aSymbol
        interval = "interval=" + anInterval
        apiKey = "apikey=" + anApiKey
        url = self.alphaVantageBaseURL + function + "&" + symbol + "&" + interval + "&" + apiKey
        return url

    def fetch_price_data(self, symbol):
        try:
            url = self.build_url("TIME_SERIES_INTRADAY", symbol, "1min", self.alphaVantageAPIKey)
            request = urllib.request.urlopen(url)
            content = request.read()
            data = json.loads(content.decode('utf-8'))
            timeSerie = data["Time Series (1min)"]
            last = next(iter(timeSerie.values()))
            value = float(last["4. close"])
        except Exception as e:
            print("Model: fetch_price_data(): {0}".format(e))
            value = 0

        return value

class Model():

    def __init__(self):
        self.read_configuration() # From config.xml file
        self.callbacks = {} # DataStruct containing the callbacks
        self.holdings = {} # DataStruct containing the current holdings and cash
        self.cashAv = 0 # Available cash in the portfolio [GBP]
        self.livePricesThread = LivePricesWebThread(self, self.webPollingPeriod)
        self.read_database()
        self.update_portfolio()

# INTERNAL FUNCTIONS

    def read_configuration(self):
        self.dbFilePath = "data/config.xml"
        self.webPollingPeriod = 15
        try:
            self.configValues = ET.parse(CONFIG_FILE_PATH).getroot()
            self.dbFilePath = self.configValues.find("TRADING_LOG_PATH").text
            self.webPollingPeriod = int(self.configValues.find("ALPHAVANTAGE_POLLING_PERIOD").text)
        except Exception as e:
            print("Model: read_configuration(): {0}".format(e))

    def read_database(self):
        try:
            self.tradingLogXMLTree = ET.parse(self.dbFilePath)
            self.log = self.tradingLogXMLTree.getroot()
        except Exception as e:
            print("Model: read_database(): {0}".format(e))
            sys.exit(1)

    def update_portfolio(self):
        for row in self.log:
            action = row.find("action").text
            amount = int(row.find("amount").text)
            symbol = row.find("symbol").text

            if action == Actions.FUNDING.name or action == Actions.DIVIDEND.name:
                self.cashAv += amount
            elif action == Actions.WITHDRAW.name:
                self.cashAv -= amount
            elif action == Actions.BUY.name:
                if symbol not in self.holdings:
                    self.holdings[symbol] = amount
                else:
                    self.holdings[symbol] += amount
            elif action == Actions.SELL.name:
                self.holdings[symbol] -= amount

# GETTERS

    def get_log_as_list(self):
        # Return a list of StockLogEntry objects
        # TODO return a list of Dict instead of using a class
        return [StockLogEntry(row.find('date').text,
                                row.find('action').text,
                                row.find('symbol').text,
                                row.find('amount').text,
                                row.find('fee').text,
                                row.find('price').text) for row in self.log]
                             
    def get_holdings(self):
        # Returns a dict {symbol: amount} for each current holding  
        return self.holdings

    def get_holding_open_price(self, symbol):
        # Return the average price paid to open the current positon of the requested stock
        sum = 0
        count = 0
        for row in self.log:
            if row.find("symbol").text == symbol and row.find("action").text == Actions.BUY.name:
                sum += float(row.find("price").text)
                count += 1
        avg = sum / count
        return round(avg, 4)

    def get_cash_available(self):
        return self.cashAv

    
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

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def update_live_price(self, priceDict):
        self.callbacks[Callbacks.UPDATE_LIVE_PRICES](priceDict)
    
