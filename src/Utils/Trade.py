from enum import Enum
import os
import sys
import inspect
import logging
import datetime

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Actions


class Trade():
    def __init__(self, date_string, action, quantity, symbol, price, fee, sdr, notes):
        try:
            self.date = datetime.datetime.strptime(date_string, '%d/%m/%Y')
            if not isinstance(action, Actions):
                raise ValueError("Invalid action")
            self.action = action
            self.quantity = quantity
            self.symbol = symbol
            self.price = price
            self.fee = fee
            self.sdr = sdr
            self.notes = notes
            self.total = self.__compute_total()
        except Exception as e:
            logging.error(e)
            raise ValueError("Invalid argument")

    def to_dict(self):
        return {
            'date': self.date.strftime('%d/%m/%Y'),
            'action': self.action.name,
            'quantity': self.quantity,
            'symbol': self.symbol,
            'price': self.price,
            'fee': self.fee,
            'stamp_duty': self.sdr,
            'notes': self.notes
        }

    @staticmethod
    def from_dict(item):
        if any(['date' not in item, 'action' not in item, 'quantity' not in item, 'symbol' not in item, 'price' not in item, 'fee' not in item, 'stamp_duty' not in item, 'notes' not in item]):
            raise ValueError('item not well formatted')

        return Trade(item['date'], Actions[item['action']], item['quantity'],
                     item['symbol'], float(item['price']), float(item['fee']),
                     float(item['stamp_duty']), str(item['notes']))

    def __compute_total(self):
        if self.action in (Actions.DEPOSIT, Actions.WITHDRAW, Actions.DIVIDEND, Actions.FEE):
            return self.quantity
        elif self.action == Actions.BUY:
            cost = (self.price / 100) * self.quantity
            return cost + self.fee + ((cost * self.sdr) / 100)
        elif self.action == Actions.SELL:
            cost = (self.price / 100) * self.quantity
            total = cost + self.fee + ((cost * self.sdr) / 100)
            return total * -1
        return 0
