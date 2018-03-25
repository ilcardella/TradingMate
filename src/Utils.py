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

# Source http://effbot.org/zone/element-lib.htm#prettyprint
def utils_indent_xml_tree(elem, level=0):
    """Indent the xml root element with "pretty" format. Can be used before writing xmlTree to a file"""
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            utils_indent_xml_tree(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i