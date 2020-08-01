from enum import Enum


class Actions(Enum):
    BUY = 1
    SELL = 2
    DEPOSIT = 3
    DIVIDEND = 4
    WITHDRAW = 5
    FEE = 6


class Messages(Enum):
    INSUF_FUNDING = "ERROR: Insufficient funding available"
    INSUF_HOLDINGS = "ERROR: Insufficient holdings available"
    INVALID_OPERATION = "ERROR: Invalid operation"
    ABOUT_MESSAGE = (
        "Creator: Alberto Cardellini\nSource: https://github.com/ilcardella/TradingMate"
    )
    ERROR_SAVE_FILE = "Error saving the log. Try again."
    ERROR_OPEN_FILE = "Error opening the file. Try again."
    UNSAVED_CHANGES = "There are unsaved changes, are you sure?"
    ERROR_SAVE_SETTINGS = "Unable to save the settings"
    WINDOW_UNSUPPORTED_ACTION = "This window does not support the selected action"
    ARE_YOU_SURE = "Are you sure?"
    UNSUPPORTED_BROKER_FEATURE = (
        "Configured stock interface does not support this feature"
    )
    SOMETHING_WRONG = "Something went wrong"


class Markets(Enum):
    LSE = "LSE"
