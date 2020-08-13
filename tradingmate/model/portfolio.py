import hashlib
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils import Actions, Messages
from . import ConfigurationManager, DatabaseHandler, Holding, StockPriceGetter, Trade


class Portfolio:
    """Represent a trading portfolio including cash available and open market positions.
    The portfolio is based on a list of trades read from the trading log
    """

    _db_handler: DatabaseHandler
    _id: str
    _name: str
    _cash_available: float = 0.0
    _cash_deposited: float = 0.0
    _holdings: Dict[str, Holding] = {}
    _unsaved_changes: bool = False
    _price_getter: StockPriceGetter

    def __init__(self, config: ConfigurationManager, trading_log_path: Path):
        # Database handler
        self._db_handler = DatabaseHandler(config, trading_log_path)
        # Create an unique id for this portfolio
        self._id = self._create_id(str(trading_log_path))
        # Portfolio name
        self._name = self._db_handler.get_trading_log_name()
        # Amount of free cash available
        self._cash_available = 0
        # Overall amount of cash deposited - withdrawed
        self._cash_deposited = 0
        # Data structure to store stock holdings: {"symbol": Holding}
        self._holdings = {}
        # Track unsaved changes
        self._unsaved_changes = False
        # Work thread that fetches stocks live prices
        self._price_getter = StockPriceGetter(config, self._on_new_price_data)
        self._price_getter.start()
        # Load the portfolio
        self._load(self._db_handler.get_trades_list())
        logging.info("Portfolio {} initialised".format(self._name))

    # PUBLIC API

    def stop(self) -> None:
        self._price_getter.shutdown()
        self._price_getter.join()
        logging.info("Portfolio {} closed".format(self._name))

    def get_id(self) -> str:
        """Return the portfolio unique id [string]"""
        return self._id

    def get_name(self) -> str:
        """Return the portfolio name [string]"""
        return self._name

    def get_portfolio_path(self) -> Path:
        """Return the complete filepath of the portfolio"""
        return self._db_handler.get_db_filepath()

    def get_cash_available(self) -> float:
        """Return the available cash quantity in the portfolio [int]"""
        return self._cash_available

    def get_cash_deposited(self) -> float:
        """Return the amount of cash deposited in the portfolio [int]"""
        return self._cash_deposited

    def get_holding_list(self) -> List[Holding]:
        """Return a list of Holding instances held in the portfolio sorted alphabetically"""
        return [self._holdings[k] for k in sorted(self._holdings)]

    def get_holding_symbols(self) -> List[str]:
        """Return a list containing the holding symbols as [string] sorted alphabetically"""
        return list(sorted(self._holdings.keys()))

    def get_holding_quantity(self, symbol: str) -> int:
        """Return the quantity held for the given symbol"""
        if symbol in self._holdings:
            return self._holdings[symbol].get_quantity()
        else:
            return 0

    def get_holding_last_price(self, symbol: str) -> Optional[float]:
        """Return the last price for the given symbol"""
        if symbol not in self._holdings:
            raise ValueError("Invalid symbol")
        return self._holdings[symbol].get_last_price()

    def get_holding_open_price(self, symbol: str) -> Optional[float]:
        """Return the last price for the given symbol"""
        if symbol not in self._holdings:
            raise ValueError("Invalid symbol")
        return self._holdings[symbol].get_open_price()

    def get_total_value(self) -> Optional[float]:
        """Return the value of the whole portfolio as cash + holdings"""
        value = self.get_holdings_value()
        if value is not None:
            return self._cash_available + value
        else:
            return None

    def get_holdings_value(self) -> Optional[float]:
        """Return the value of the holdings held in the portfolio"""
        holdingsValue = 0.0
        for holding in self._holdings.values():
            value = holding.get_value()
            if value is not None:
                holdingsValue += value
            else:
                return None
        return holdingsValue

    def get_portfolio_pl(self) -> Optional[float]:
        """
        Return the profit/loss in £ of the portfolio over the deposited cash
        """
        value = self.get_total_value()
        invested = self.get_cash_deposited()
        if value is None or invested is None:
            return None
        return value - invested

    def get_portfolio_pl_perc(self) -> Optional[float]:
        """
        Return the profit/loss in % of the portfolio over deposited cash
        """
        pl = self.get_portfolio_pl()
        invested = self.get_cash_deposited()
        if pl is None or invested is None or invested < 1:
            return None
        return (pl / invested) * 100

    def get_open_positions_pl(self) -> Optional[float]:
        """
        Return the sum profit/loss in £ of the current open positions
        """
        try:
            total_pl = 0.0
            for holding in self._holdings.values():
                pl = holding.get_profit_loss()
                if pl is None:
                    return None
                total_pl += pl
            return total_pl
        except Exception as e:
            logging.error(e)
            raise RuntimeError("Unable to compute holgings profit/loss")

    def get_open_positions_pl_perc(self) -> Optional[float]:
        """
        Return the sum profit/loss in % of the current open positions
        """
        try:
            costSum = 0.0
            valueSum = 0.0
            for holding in self._holdings.values():
                cost = holding.get_cost()
                value = holding.get_value()
                if cost is None or value is None:
                    return None
                costSum += cost
                valueSum += value
            if costSum < 1:
                return None
            return ((valueSum - costSum) / costSum) * 100
        except Exception as e:
            logging.error(e)
            raise RuntimeError("Unable to compute holdings profit/loss percentage")

    def has_unsaved_changes(self) -> bool:
        """Return True if the portfolio has unsaved changes, False othersise"""
        return self._unsaved_changes

    def get_trade_history(self) -> List[Trade]:
        """Return the trade history as a list"""
        return self._db_handler.get_trades_list()

    def add_trade(self, new_trade: Trade) -> None:
        """Add a new trade into the Portfolio"""
        current_list = self._db_handler.get_trades_list()
        # Build the list of trades happened before and after the new trade to validate
        # If trade date match with existing trade, the new trade is appended after
        older_trades = [trade for trade in current_list if trade.date <= new_trade.date]
        newer_trades = [trade for trade in current_list if trade.date > new_trade.date]
        # Build the new trade list inserting the new trade
        new_trade_list = older_trades + [new_trade] + newer_trades
        self._validate_trade_list(new_trade_list)
        self._db_handler.add_trade(new_trade)
        self._load(self._db_handler.get_trades_list())
        self._unsaved_changes = True

    def delete_trade(self, trade_id: str) -> None:
        """Remove a trade from the Portfolio"""
        # Validate the trade list removing the trade
        new_trade_list = [
            t for t in self._db_handler.get_trades_list() if t.id != trade_id
        ]
        self._validate_trade_list(new_trade_list)
        self._db_handler.delete_trade(trade_id)
        self._load(self._db_handler.get_trades_list())
        self._unsaved_changes = True

    def save_portfolio(self, filepath: Path) -> None:
        """Save the portfolio at the given filepath"""
        self._db_handler.write_data(filepath)
        self._unsaved_changes = False

    # PRIVATE API

    def _clear(self) -> None:
        """
        Reset the Portfolio clearing all data
        """
        self._cash_available = 0
        self._cash_deposited = 0
        self._holdings.clear()
        self._price_getter.reset()
        logging.info("Portfolio {} cleared".format(self._name))

    def _load_from_trade_list(
        self, trades: List[Trade]
    ) -> Tuple[float, float, Dict[str, Holding]]:
        # Scan the trades list and build the portfolio in buffer variables
        # This allow us to validate each trade without changing the current state
        cash_available = 0.0
        cash_deposited = 0.0
        holdings: Dict[str, Holding] = {}
        for trade in trades:
            self._trade_is_allowed(trade, cash_available, holdings)
            # Trade is valid so update buffers based on action type
            if trade.action == Actions.DEPOSIT or trade.action == Actions.DIVIDEND:
                cash_available += trade.quantity
                if trade.action == Actions.DEPOSIT:
                    cash_deposited += trade.quantity
            elif trade.action == Actions.WITHDRAW:
                cash_available -= trade.quantity
                cash_deposited -= trade.quantity
            elif trade.action == Actions.BUY:
                if trade.symbol not in holdings:
                    holdings[trade.symbol] = Holding(trade.symbol, int(trade.quantity))
                else:
                    holdings[trade.symbol].add_quantity(int(trade.quantity))
                cost = (trade.price / 100) * trade.quantity
                tax = (trade.sdr * cost) / 100
                totalCost = cost + tax + trade.fee
                cash_available -= totalCost
            elif trade.action == Actions.SELL:
                holdings[trade.symbol].add_quantity(int(-trade.quantity))  # negative
                if holdings[trade.symbol].get_quantity() < 1:
                    del holdings[trade.symbol]
                profit = ((trade.price / 100) * trade.quantity) - trade.fee
                cash_available += profit
            elif trade.action == Actions.FEE:
                cash_available -= trade.quantity
        return cash_deposited, cash_available, holdings

    def _load(self, trades_list: List[Trade]) -> None:
        """
        Load the portfolio from the database trade list
        """
        try:
            cash_deposited, cash_available, holdings = self._load_from_trade_list(
                trades_list
            )
            # All trades were valid so do the actual load of this portfolio
            self._clear()
            self._cash_available = cash_available
            self._cash_deposited = cash_deposited
            self._holdings = holdings
            # Update symbol list of the worker thread that fetches prices
            self._price_getter.set_symbol_list(self.get_holding_symbols())
            # Compute the average open price of each holding
            for symbol in self._holdings.keys():
                self._holdings[symbol].set_open_price(
                    self._compute_avg_holding_open_price(symbol, trades_list)
                )
            # If available set the last price of each holding
            for symbol, price in self._price_getter.get_last_data().items():
                self._holdings[symbol].set_last_price(price)
            logging.info("Portfolio {} reloaded successfully".format(self._name))
        except Exception as e:
            logging.error(e)
            raise RuntimeError(f"Unable to load the portfolio: {e}")

    def _compute_avg_holding_open_price(
        self, symbol: str, trades_list: List[Trade]
    ) -> float:
        """
        Return the average price paid to open the current positon of the requested stock.
        Starting from the end of the history log, find the BUY transaction that led to
        to have the current quantity, compute then the average price of these transactions
        """
        total_cost = 0.0
        count = 0
        target = self.get_holding_quantity(symbol)
        if target == 0:
            raise ValueError("Market {} not in current holdings".format(symbol))
        for trade in trades_list[::-1]:  # reverse order
            if trade.symbol == symbol and trade.action == Actions.BUY:
                target -= int(trade.quantity)
                total_cost += trade.price * int(trade.quantity)
                count += int(trade.quantity)
                if target <= 0:
                    break
        avg = total_cost / count
        return round(avg, 4)

    def _validate_trade_list(self, trade_list: List[Trade]) -> None:
        """
        Validate the trade list
        """
        # Verify that the new list is valid
        deposited, available, holdings = self._load_from_trade_list(trade_list)

    def _trade_is_allowed(
        self, new_trade: Trade, cash_available: float, holdings: Dict[str, Holding]
    ) -> bool:
        """
        Throws RuntimeError is the trade is allowed basedo one the given quantities
        """
        if new_trade.action == Actions.WITHDRAW or new_trade.action == Actions.FEE:
            if new_trade.quantity > cash_available:
                logging.warning(
                    "Portfolio {}: {}".format(self._name, Messages.INSUF_FUNDING.value)
                )
                raise RuntimeError(Messages.INSUF_FUNDING.value)
        elif new_trade.action == Actions.BUY:
            cost = (new_trade.price * new_trade.quantity) / 100  # in £
            fee = new_trade.fee
            tax = (new_trade.sdr * cost) / 100
            totalCost = cost + fee + tax
            if totalCost > cash_available:
                logging.warning(
                    "Portfolio {}: {}".format(self._name, Messages.INSUF_FUNDING.value)
                )
                raise RuntimeError(Messages.INSUF_FUNDING.value)
        elif new_trade.action == Actions.SELL:
            quantity = (
                holdings[new_trade.symbol].get_quantity()
                if new_trade.symbol in holdings
                else 0
            )
            if new_trade.quantity > quantity:
                logging.warning(
                    "Portfolio {}: {}".format(self._name, Messages.INSUF_HOLDINGS.value)
                )
                raise RuntimeError(Messages.INSUF_HOLDINGS.value)
        return True

    def _create_id(self, seed: str) -> str:
        """Create and return an unique id from the seed"""
        seed += str(time.time())
        return hashlib.sha1(seed.encode("utf-8")).hexdigest()

    # PRICE GETTER WORK THREAD

    def _on_new_price_data(self) -> None:
        priceDict = self._price_getter.get_last_data()
        for symbol, price in priceDict.items():
            if symbol in self._holdings:
                self._holdings[symbol].set_last_price(price)

    def on_manual_refresh_live_data(self) -> None:
        logging.info("Portfolio {}: manual refresh of data".format(self._name))
        if self._price_getter.is_enabled():
            self._price_getter.cancel_timeout()
        else:
            self._price_getter.force_single_run()

    def set_auto_refresh(self, enabled: bool = True) -> None:
        logging.info(
            "Portfolio {}: price auto refresh set to {}".format(self._name, enabled)
        )
        self._price_getter.enable(enabled)

    def get_auto_refresh_enabled(self) -> bool:
        return self._price_getter.is_enabled()
