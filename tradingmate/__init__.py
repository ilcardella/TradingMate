from tradingmate.TradingMate import TradingMate


def main():
    # Initialise the business logic
    tm = TradingMate()
    from tradingmate.UI.gtk.UIHandler import UIHandler

    UIHandler(tm).start()
