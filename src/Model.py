from .TaskThread import TaskThread
from .Utils import *

import sys
from enum import Enum
import xml.etree.ElementTree as ET
from xml.dom import minidom
import threading
import time
import sys
import urllib.request
import json

# Globals
CONFIG_FILE_PATH = "data/config_private.xml" # Change this to data/config.xml
WEB_POLLING_SECONDS = 15 #Seconds

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
            print("LivePricesWebThread:read_configuration() {0}".format(e))
            sys.exit(1)

    def task(self):
        priceDict = {}
        symbolList = self.model.get_holdings().keys()
        for symbol in symbolList:
            if not self._finished.isSet():
                value = self.fetch_price_data(symbol)
                self._timeout.wait(1)
                if value is not None:
                    priceDict[symbol] = value
        if not self._finished.isSet():
            self.model.update_live_price(priceDict)

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
            value = None
        return value

    def build_url(self, aLength, aSymbol, anInterval, anApiKey):
        function = "function=" + aLength
        symbol = "symbol=" + aSymbol
        interval = "interval=" + anInterval
        apiKey = "apikey=" + anApiKey
        url = self.alphaVantageBaseURL + function + "&" + symbol + "&" + interval + "&" + apiKey
        return url

class Model():

    def __init__(self):
        self.read_configuration() # From config.xml file
        self.callbacks = {} # DataStruct containing the callbacks
        self.holdings = {} # DataStruct containing the current holdings
        self.cashAvailable = 0 # Available cash in the portfolio [GBP]
        self.lastLiveData = {} # Buffer to store the latest live data fetched from the web api
        self.livePricesThread = LivePricesWebThread(self, self.webPollingPeriod)
        self.read_database(self.dbFilePath)
        self.update_portfolio()

# INTERNAL FUNCTIONS

    def read_configuration(self):
        self.dbFilePath = "data/trading_log.xml"
        self.webPollingPeriod = 15
        try:
            self.configValues = ET.parse(CONFIG_FILE_PATH).getroot()
            self.dbFilePath = self.configValues.find("TRADING_LOG_PATH").text
            self.webPollingPeriod = int(self.configValues.find("ALPHAVANTAGE_POLLING_PERIOD").text)
        except Exception as e:
            print("Model: read_configuration(): {0}".format(e))

    def read_database(self, filepath):
        try:
            self.tradingLogXMLTree = ET.parse(filepath)
            self.log = self.tradingLogXMLTree.getroot()
        except Exception as e:
            print("Model: Error reading database! {0}".format(e))
            self.log = ET.Element("log")

    def update_portfolio(self):
        self.cashAvailable = 0
        self.holdings.clear()
        for row in self.log:
            action = row.find("action").text
            amount = float(row.find("amount").text)
            symbol = row.find("symbol").text
            price = float(row.find("price").text)
            fee = float(row.find("fee").text)
            sd = float(row.find("stamp_duty").text)

            if action == Actions.DEPOSIT.name or action == Actions.DIVIDEND.name:
                self.cashAvailable += amount
            elif action == Actions.WITHDRAW.name:
                self.cashAvailable -= amount
            elif action == Actions.BUY.name:
                if symbol not in self.holdings:
                    self.holdings[symbol] = amount
                else:
                    self.holdings[symbol] += amount
                cost = (price/100) * amount
                tax = (sd * cost) / 100
                totalCost = cost + tax + fee
                self.cashAvailable -= totalCost
            elif action == Actions.SELL.name:
                self.holdings[symbol] -= amount
                if self.holdings[symbol] < 1:
                    del self.holdings[symbol]
                profit = ((price/100) * amount) - fee
                self.cashAvailable += profit
    
    def add_entry_to_db(self, logEntry):
        row = ET.SubElement(self.log, "row")
        date = ET.SubElement(row, "date")
        date.text = str(logEntry["date"]).strip()
        action = ET.SubElement(row, "action")
        action.text = str(logEntry["action"]).strip()
        symbol = ET.SubElement(row, "symbol")
        symbol.text = str(logEntry["symbol"]).strip()
        amount = ET.SubElement(row, "amount")
        amount.text = str(logEntry["amount"]).strip()
        price = ET.SubElement(row, "price")
        price.text = str(logEntry["price"]).strip()
        fee = ET.SubElement(row, "fee")
        fee.text = str(logEntry["fee"]).strip()
        sd = ET.SubElement(row, "stamp_duty")
        sd.text = str(logEntry["stamp_duty"]).strip()
    
    def remove_entry_from_db(self, logEntry):
        self.log.remove(logEntry)

    def reset(self, filepath=None):
        self.read_configuration() # From config.xml file
        self.holdings.clear() # DataStruct containing the current holdings
        self.cashAvailable = 0 # Available cash in the portfolio [GBP]
        self.lastLiveData.clear() # Buffer to store the latest live data fetched from the web api
        if filepath is not None:
            self.dbFilePath = filepath
        self.read_database(self.dbFilePath)
        self.update_portfolio()

# GETTERS

    def get_log_as_list(self):
        # return a list of Dict with the log data
        listOfEntries = []
        for row in self.log:
            d = {}
            d["date"] = row.find('date').text
            d["action"] = row.find('action').text
            d["symbol"] = row.find('symbol').text
            d["amount"] = float(row.find('amount').text) if row.find('amount').text is not None else 0
            d["price"] = float(row.find('price').text)  if row.find('price').text is not None else 0.0
            d["fee"] = float(row.find('fee').text)  if row.find('fee').text is not None else 0.0
            d["stamp_duty"] = float(row.find('stamp_duty').text) if row.find('stamp_duty').text is not None else 0.0
            listOfEntries.append(d)
        return listOfEntries
                             
    def get_holdings(self):
        # Returns a dict {symbol: amount} for each current holding  
        return self.holdings

    def get_holding_open_price(self, symbol):
        """Return the average price paid to open the current positon of the requested stock"""
        # Starting from the end of the history log, find the BUY transaction that led to
        # to have the current amount, compute then the average price of these transactions
        sum = 0
        count = 0
        targetAmount = self.get_holdings()[symbol]
        for row in self.log[::-1]: # reverse order
            action = row.find("action").text
            sym = row.find("symbol").text
            price = float(row.find("price").text)
            amount = float(row.find("amount").text)
            if sym == symbol and action == Actions.BUY.name:
                targetAmount -= amount
                sum += price * amount
                count += amount
                if targetAmount <= 0:
                    break
        avg = sum / count
        return round(avg, 4)

    def get_cash_available(self):
        return self.cashAvailable

    def get_invested_amount(self):
        """Return the total invested amount in the portfolio"""
        amount = 0.0
        for row in self.log:
            action = row.find("action").text
            if action == Actions.DEPOSIT.name:
                amount += float(row.find("amount").text)
            elif action == Actions.WITHDRAW.name:
                amount -= float(row.find("amount").text)
        return amount
            
    
# INTERFACES

    def start(self):
        self.livePricesThread.start()

    def stop_application(self):
        self.livePricesThread.shutdown()
        self.write_log_to_file(self.dbFilePath)

    def write_log_to_file(self, filepath):
        # write the in memory db to a file
        utils_indent_xml_tree(self.log)
        newTree = ET.ElementTree(self.log)
        newTree.write(filepath, xml_declaration=True, encoding='utf-8', method="xml")

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def add_new_trade(self, newTrade):
        result = {"success":True,"message":"ok"}
        try:
            self.add_entry_to_db(newTrade)
            self.update_portfolio()
        except Exception:
            result["success"] = False
            result["message"] = "Error: Invalid operation"
        
        return result

    def update_live_price(self, priceDict):
        # Replace None values with the last valid data
        for symbol in priceDict.keys():
            if priceDict[symbol] is None and symbol in self.lastLiveData:
                priceDict[symbol] = self.lastLiveData[symbol]

        self.lastLiveData = priceDict # Store locally
        self.callbacks[Callbacks.UPDATE_LIVE_PRICES](priceDict) # Call callback
    
    def set_auto_refresh(self, enabled):
        self.livePricesThread.enable(enabled)

    def on_manual_refresh_live_data(self):
        if self.livePricesThread.is_enabled():
            self.livePricesThread.cancel_timeout()
        else:
            self.livePricesThread.force_single_run()

    def save_log_file(self, filepath):
        result = {"success":True,"message":"ok"}
        try:
            self.write_log_to_file(filepath)
        except Exception:
            result["success"] = False
            result["message"] = "Error saving the log. Try again."
        return result
    
    def open_log_file(self, filepath):
        result = {"success":True,"message":"ok"}
        try:
            self.reset(filepath)
        except Exception:
            result["success"] = False
            result["message"] = "Error opening the file. Try again."
        return result

