from enum import Enum

# Enumerations

class Callbacks(Enum):
    UPDATE_LIVE_PRICES = 1
    ON_CLOSE_VIEW_EVENT = 2

class Actions(Enum):
    BUY = 1
    SELL = 2
    DEPOSIT = 3
    DIVIDEND = 4
    WITHDRAW = 5