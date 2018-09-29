from enum import Enum

# Enumerations

class Callbacks(Enum):
    UPDATE_LIVE_PRICES = 1
    ON_CLOSE_VIEW_EVENT = 2
    ON_MANUAL_REFRESH_EVENT = 3
    ON_NEW_TRADE_EVENT = 4
    ON_SET_AUTO_REFRESH_EVENT = 5
    ON_OPEN_LOG_FILE_EVENT = 6
    ON_SAVE_LOG_FILE_EVENT = 7
    ON_DELETE_LAST_TRADE_EVENT = 8
    ON_START_AUTOTRADING = 9
    ON_STOP_AUTOTRADING = 10

class Actions(Enum):
    BUY = 1
    SELL = 2
    DEPOSIT = 3
    DIVIDEND = 4
    WITHDRAW = 5

class Messages(Enum):
    INSUF_FUNDING = "ERROR: Insufficient funding available"
    INSUF_HOLDINGS = "ERROR: Insufficient holdings available"
    INVALID_OPERATION = "ERROR: Invalid operation"
    ABOUT_MESSAGE = "Creator: Alberto Cardellini\nEmail: albe.carde@gmail.com"
    ERROR_SAVE_FILE = "Error saving the log. Try again."
    ERROR_OPEN_FILE = "Error opening the file. Try again."

class Markets(Enum):
    LSE = "LON"
