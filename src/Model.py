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
        return [StockLogEntry(row[0].text,row[1].text,row[2].text,row[3].text,row[4].text,row[5].text) for row in self.log]
