import sys
from enum import Enum
import xml.etree.ElementTree as ET

# Enumerations
class Actions(Enum):
    BUY = 1
    SELL = 2
    FUNDING = 3
    DIVIDEND = 4

# Globals
DB_FILE_PATH = "data/trading_log.xml"

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

class Model():

    def __init__(self):
        self.read_configuration()
        self.read_database()

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

    def add_log_entry(self, logEntry):
        self.log.append(logEntry)
        self.xmlTree.write(self.dbFilename)
    
    def remove_log_entry(self, logEntry):
        self.log.remove(logEntry)
        self.xmlTree.write(self.dbFilename)

    def get_log_as_list(self):
        return [StockLogEntry(row.find('date').text,
                                row.find('action').text,
                                row.find('symbol').text,
                                row.find('amount').text,
                                row.find('fee').text,
                                row.find('price').text) for row in self.log]
