from .trading_mate import TradingMate


def main() -> None:
    # Initialise the business logic
    tm = TradingMate()
    from .ui.gtk import UIHandler

    UIHandler(tm).start()
