import os
import inspect
import sys
import logging

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from .Holding import Holding
from Utils.Utils import Actions, Messages, Callbacks
from .StockPriceGetter import StockPriceGetter

class Portfolio():
    def __init__(self, name, config):
        # Portfolio name
        self._name = name
        # Amount of free cash available
        self._cash_available = 0
        # Overall amount of cash deposited - withdrawed
        self._cash_deposited = 0
        # Data structure to store stock holdings: {"symbol": Holding}
        self._holdings = {}
        # DataStruct containing the callbacks
        self.callbacks = {}
        # Work thread that fetches stocks live prices
        self.price_getter = StockPriceGetter(config, self.on_new_price_data)
        logging.info('Portfolio initialised')

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def start(self, trades_list):
        self.reload(trades_list)
        self.price_getter.start()
        logging.info('Portfolio started')

    def stop(self):
        self.price_getter.shutdown()
        self.price_getter.join()
        logging.info('Portfolio stopped')

# GETTERS

    def get_name(self):
        """Return the portfolio name [string]"""
        return self._name

    def get_cash_available(self):
        """Return the available cash quantity in the portfolio [int]"""
        return self._cash_available

    def get_cash_deposited(self):
        """Return the amount of cash deposited in the portfolio [int]"""
        return self._cash_deposited

    def get_holding_list(self):
        """Return a list of Holding instances held in the portfolio sorted alphabetically"""
        return [self._holdings[k] for k in sorted(self._holdings)]

    def get_holding_symbols(self):
        """Return a list containing the holding symbols as [string] sorted alphabetically"""
        return list(sorted(self._holdings.keys()))

    def get_holding_quantity(self, symbol):
        """Return the quantity held for the given symbol"""
        if symbol in self._holdings:
            return self._holdings[symbol].get_quantity()
        else:
            return 0

    def get_holding_last_price(self, symbol):
        """Return the last price for the given symbol"""
        if symbol not in self._holdings:
            raise ValueError('Invalid symbol')
        return self._holdings[symbol].get_last_price()

    def get_holding_open_price(self, symbol):
        """Return the last price for the given symbol"""
        if symbol not in self._holdings:
            raise ValueError('Invalid symbol')
        return self._holdings[symbol].get_open_price()

    def get_total_value(self):
        """Return the value of the whole portfolio as cash + holdings"""
        value = self.get_holdings_value()
        if value is not None:
            return self._cash_available + value
        else:
            return None

    def get_holdings_value(self):
        """Return the value of the holdings held in the portfolio"""
        holdingsValue = 0
        for holding in self._holdings.values():
            if holding.get_value() is not None:
                holdingsValue += holding.get_value()
            else:
                return None
        return holdingsValue

    def get_portfolio_pl(self):
        """
        Return the profit/loss in £ of the portfolio over the deposited cash
        """
        value = self.get_total_value()
        invested = self.get_cash_deposited()
        if value is None or invested is None:
            return None
        return value - invested

    def get_portfolio_pl_perc(self):
        """
        Return the profit/loss in % of the portfolio over deposited cash
        """
        pl = self.get_portfolio_pl()
        invested = self.get_cash_deposited()
        if pl is None or invested is None or invested < 1:
            return None
        return (pl / invested) * 100

    def get_open_positions_pl(self):
        """
        Return the sum profit/loss in £ of the current open positions
        """
        try:
            sum = 0
            for holding in self._holdings.values():
                pl = holding.get_profit_loss()
                if pl is None:
                    return None
                sum += pl
            return sum
        except Exception as e:
            logging.error(e)
            raise RuntimeError('Unable to compute holgings profit/loss')

    def get_open_positions_pl_perc(self):
        """
        Return the sum profit/loss in % of the current open positions
        """
        try:
            costSum = 0
            valueSum = 0
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
            raise RuntimeError('Unable to compute holdings profit/loss percentage')

# FUNCTIONS

    def clear(self):
        """
        Reset the Portfolio clearing all data
        """
        self._cash_available = 0
        self._cash_deposited = 0
        self._holdings.clear()
        self.price_getter.reset()
        logging.info('Portfolio cleared')

    def reload(self, trades_list):
        """
        Load the portfolio from the given trade list
        """
        try:
            # Reset the portfolio
            self.clear()
            # Scan the trades list and build the portfolio
            for trade in trades_list:
                if trade.action == Actions.DEPOSIT or trade.action == Actions.DIVIDEND:
                    self._cash_available += trade.quantity
                    if trade.action == Actions.DEPOSIT:
                        self._cash_deposited += trade.quantity
                elif trade.action == Actions.WITHDRAW:
                    self._cash_available -= trade.quantity
                    self._cash_deposited -= trade.quantity
                elif trade.action == Actions.BUY:
                    if trade.symbol not in self._holdings:
                        self._holdings[trade.symbol] = Holding(trade.symbol, trade.quantity)
                    else:
                        self._holdings[trade.symbol].add_quantity(trade.quantity)
                    cost = (trade.price/100) * trade.quantity
                    tax = (trade.sdr * cost) / 100
                    totalCost = cost + tax + trade.fee
                    self._cash_available -= totalCost
                elif trade.action == Actions.SELL:
                    self._holdings[trade.symbol].add_quantity(-trade.quantity) # negative
                    if self._holdings[trade.symbol].get_quantity() < 1:
                        del self._holdings[trade.symbol]
                    profit = ((trade.price/100) * trade.quantity) - trade.fee
                    self._cash_available += profit
                elif trade.action == Actions.FEE:
                    self._cash_available -= trade.quantity
            self.price_getter.set_symbol_list(self.get_holding_symbols())
            for symbol in self._holdings.keys():
                self._holdings[symbol].set_open_price(self.compute_avg_holding_open_price(symbol, trades_list))
            for symbol, price in self.price_getter.get_last_data().items():
                self._holdings[symbol].set_last_price(price)
            logging.info('Portfolio reloaded successfully')
        except Exception as e:
            logging.error(e)
            raise RuntimeError('Unable to reload the portfolio')

    def compute_avg_holding_open_price(self, symbol, trades_list):
        """
        Return the average price paid to open the current positon of the requested stock.
        Starting from the end of the history log, find the BUY transaction that led to
        to have the current quantity, compute then the average price of these transactions
        """
        sum = 0
        count = 0
        target = self.get_holding_quantity(symbol)
        if target == 0:
            return None
        for trade in trades_list[::-1]:  # reverse order
            if trade.symbol == symbol and trade.action == Actions.BUY:
                target -= trade.quantity
                sum += trade.price * trade.quantity
                count += trade.quantity
                if target <= 0:
                    break
        avg = sum / count
        return round(avg, 4)

    def is_trade_valid(self, newTrade):
        """
        Validate the new Trade request against the current Portfolio
        """
        if newTrade.action == Actions.WITHDRAW or newTrade.action == Actions.FEE:
            if newTrade.quantity > self.get_cash_available():
                logging.warning(Messages.INSUF_FUNDING.value)
                raise RuntimeError(Messages.INSUF_FUNDING.value)
        elif newTrade.action == Actions.BUY:
            cost = (newTrade.price * newTrade.quantity) / 100  # in £
            fee = newTrade.fee
            tax = (newTrade.sdr * cost) / 100
            totalCost = cost + fee + tax
            if totalCost > self.get_cash_available():
                logging.warning(Messages.INSUF_FUNDING.value)
                raise RuntimeError(Messages.INSUF_FUNDING.value)
        elif newTrade.action == Actions.SELL:
            if newTrade.quantity > self.get_holding_quantity(newTrade.symbol):
                logging.warning(Messages.INSUF_HOLDINGS.value)
                raise RuntimeError(Messages.INSUF_HOLDINGS.value)
        logging.info('Portfolio - trade validated')
        return True

# PRICE GETTER WORK THREAD

    def on_new_price_data(self):
        logging.info('Portfolio - new live price available')
        priceDict = self.price_getter.get_last_data()
        for symbol, price in priceDict.items():
            if symbol in self._holdings:
                self._holdings[symbol].set_last_price(price)
        self.callbacks[Callbacks.UPDATE_LIVE_PRICES]()

    def on_manual_refresh_live_data(self):
        logging.info('Portfolio - manual refresh live price')
        if self.price_getter.is_enabled():
            self.price_getter.cancel_timeout()
        else:
            self.price_getter.force_single_run()

    def set_auto_refresh(self, enabled):
        logging.info('Portfolio - live price auto refresh: {}'.format(enabled))
        self.price_getter.enable(enabled)
