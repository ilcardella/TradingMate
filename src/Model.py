from .TaskThread import TaskThread
from .Utils import Messages, Actions, Callbacks
from .Portfolio import Portfolio

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

class LivePricesWebThread(TaskThread):

    def __init__(self, model, updatePeriod):
        TaskThread.__init__(self, updatePeriod)
        self.model = model
        self._read_configuration()
        self.lastData = {}
        self.symbolList = []

    def _read_configuration(self):
        try:
            self.configValues = ET.parse(CONFIG_FILE_PATH).getroot()
            self.alphaVantageAPIKey = self.configValues.find("ALPHAVANTAGE_API_KEY").text
            self.alphaVantageBaseURL = self.configValues.find("ALPHAVANTAGE_BASE_URL").text
            # add other config parameters
        except Exception as e:
            print("LivePricesWebThread: _read_configuration() {0}".format(e))
            sys.exit(1)

    def task(self):
        priceDict = {}
        for symbol in self.symbolList:
            if not self._finished.isSet():
                value = self._fetch_price_data(symbol)
                self._timeout.wait(1) # Wait 1 sec as suggested by AlphaVantage support
                if value is not None:
                    priceDict[symbol] = value
        if not self._finished.isSet():
            self.lastData = priceDict # Store internally
            self.model.on_new_price_data() # Notify the model

    def _fetch_price_data(self, symbol):
        try:
            url = self._build_url("TIME_SERIES_DAILY", symbol, "5min", self.alphaVantageAPIKey)
            request = urllib.request.urlopen(url, timeout=10)
            content = request.read()
            data = json.loads(content.decode('utf-8'))
            timeSerie = data["Time Series (Daily)"]
            last = next(iter(timeSerie.values()))
            value = float(last["4. close"])
        except Exception:
            print("LivePricesWebThread: _fetch_price_data(): {0}".format(url))
            value = None
        return value

    def _build_url(self, aLength, aSymbol, anInterval, anApiKey):
        function = "function=" + aLength
        symbol = "symbol=" + aSymbol
        apiKey = "apikey=" + anApiKey
        url = self.alphaVantageBaseURL + "?" + function + "&" + symbol + "&" + apiKey
        return url

    def get_last_data(self):
        return self.lastData

    def set_symbol_list(self, list):
        self.symbolList = list

class Model():

    def __init__(self):
        self._read_configuration() # From config.xml file
        self._read_database(self.dbFilePath)
        self.callbacks = {} # DataStruct containing the callbacks
        self.livePricesThread = LivePricesWebThread(self, self.webPollingPeriod)
        self.portfolio = Portfolio("Portfolio1")

# INTERNAL FUNCTIONS

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def _read_configuration(self):
        self.dbFilePath = "data/trading_log.xml"
        self.webPollingPeriod = 15
        try:
            self.configValues = ET.parse(CONFIG_FILE_PATH).getroot()
            self.dbFilePath = self.configValues.find("TRADING_LOG_PATH").text
            self.webPollingPeriod = int(self.configValues.find("ALPHAVANTAGE_POLLING_PERIOD").text)
        except Exception as e:
            print("Model: _read_configuration(): {0}".format(e))

    def _read_database(self, filepath):
        try:
            self.tradingLogXMLTree = ET.parse(filepath)
            self.log = self.tradingLogXMLTree.getroot()
        except Exception as e:
            print("Model: Error reading database! {0}".format(e))
            self.log = ET.Element("log")

    def _update_portfolio(self):
        """Scan the database and update the Portfolio instance"""
        cashAvailable = 0.0
        investedAmount = 0.0
        holdings = {}
        for row in self.log:
            action = row.find("action").text
            amount = float(row.find("amount").text)
            symbol = row.find("symbol").text
            price = float(row.find("price").text)
            fee = float(row.find("fee").text)
            sd = float(row.find("stamp_duty").text)

            if action == Actions.DEPOSIT.name or action == Actions.DIVIDEND.name:
                cashAvailable += amount
                if action == Actions.DEPOSIT.name:
                    investedAmount += amount
            elif action == Actions.WITHDRAW.name:
                cashAvailable -= amount
                investedAmount -= amount
            elif action == Actions.BUY.name:
                if symbol not in holdings:
                    holdings[symbol] = amount
                else:
                    holdings[symbol] += amount
                cost = (price/100) * amount
                tax = (sd * cost) / 100
                totalCost = cost + tax + fee
                cashAvailable -= totalCost
            elif action == Actions.SELL.name:
                holdings[symbol] -= amount
                if holdings[symbol] < 1:
                    del holdings[symbol]
                profit = ((price/100) * amount) - fee
                cashAvailable += profit

        self.portfolio.clear()
        for symbol, amount in holdings.items():
            self.portfolio.update_holding_amount(symbol, amount)
            self.portfolio.update_holding_open_price(symbol, self.get_holding_open_price(symbol))
        self.portfolio.set_invested_amount(investedAmount)
        self.portfolio.set_cash_available(cashAvailable)
        for symbol, price in self.livePricesThread.get_last_data().items():
            self.portfolio.update_holding_last_price(symbol, price)
    
    def _add_entry_to_db(self, logEntry):
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
    
    def _remove_entry_from_db(self, logEntry):
        # TODO
        self.log.remove(logEntry)

    def _reset(self, filepath=None):
        self._read_configuration() # From config.xml file
        if filepath is not None:
            self.dbFilePath = filepath
        self._read_database(self.dbFilePath)
        self._update_portfolio()

    def _write_log_to_file(self, filepath):
        # write the in memory db to a file
        self._utils_indent_xml_tree(self.log)
        newTree = ET.ElementTree(self.log)
        newTree.write(filepath, xml_declaration=True, encoding='utf-8', method="xml")

    # Source http://effbot.org/zone/element-lib.htm#prettyprint
    def _utils_indent_xml_tree(self, elem, level=0):
        """Indent the xml root element with "pretty" format. Can be used before writing xmlTree to a file"""
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._utils_indent_xml_tree(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

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

    def get_holding_open_price(self, symbol):
        """Return the average price paid to open the current positon of the requested stock"""
        # Starting from the end of the history log, find the BUY transaction that led to
        # to have the current amount, compute then the average price of these transactions
        sum = 0
        count = 0
        targetAmount = self.portfolio.get_holding_amount(symbol)
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
            
    def get_portfolio(self):
        """Return the portfolio as instance of Portfolio class"""
        return self.portfolio

    def get_db_filepath(self):
        return self.dbFilePath

# INTERFACES

    def start(self):
        self._update_portfolio()
        self.livePricesThread.set_symbol_list(self.portfolio.get_holding_symbols())
        self.livePricesThread.start()

    def stop_application(self):
        self.livePricesThread.shutdown()
        self.livePricesThread.join()
        self._write_log_to_file(self.dbFilePath)

    def add_new_trade(self, newTrade):
        result = {"success":True,"message":"ok"}
        try:
            self._add_entry_to_db(newTrade)
            self._update_portfolio()
            self.livePricesThread.set_symbol_list(self.portfolio.get_holding_symbols())
        except Exception:
            result["success"] = False
            result["message"] = Messages.INVALID_OPERATION.value
        return result

    def on_new_price_data(self):
        priceDict = self.livePricesThread.get_last_data()
        for symbol, price in priceDict.items():
            self.portfolio.update_holding_last_price(symbol, price)
        self.callbacks[Callbacks.UPDATE_LIVE_PRICES]() # Call callback
    
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
            self._write_log_to_file(filepath)
        except Exception:
            result["success"] = False
            result["message"] = Messages.ERROR_SAVE_FILE
        return result
    
    def open_log_file(self, filepath):
        result = {"success":True,"message":"ok"}
        try:
            self._reset(filepath)
        except Exception:
            result["success"] = False
            result["message"] = Messages.ERROR_OPEN_FILE
        return result

