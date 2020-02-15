from enum import Enum
import os
import sys
import inspect
import logging
import time
import datetime
import hashlib

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Actions


class Trade:
    def __init__(
        self, date_string, action, quantity, symbol, price, fee, sdr, notes, id=None
    ):
        try:
            self.date = datetime.datetime.strptime(date_string, "%d/%m/%Y")
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
            self.id = self._create_id() if id is None else id
        except Exception as e:
            logging.error(e)
            raise ValueError("Invalid argument")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%d/%m/%Y"),
            "action": self.action.name,
            "quantity": self.quantity,
            "symbol": self.symbol,
            "price": self.price,
            "fee": self.fee,
            "stamp_duty": self.sdr,
            "notes": self.notes,
        }

    def to_string(self):
        return (
            f"{self.date}_{self.action.name}_{self.quantity}_{self.symbol}_{self.price}"
        )

    @staticmethod
    def from_dict(item):
        if any(
            [
                "id" not in item,
                "date" not in item,
                "action" not in item,
                "quantity" not in item,
                "symbol" not in item,
                "price" not in item,
                "fee" not in item,
                "stamp_duty" not in item,
                "notes" not in item,
            ]
        ):
            raise ValueError("item not well formatted")

        return Trade(
            item["date"],
            Actions[item["action"]],
            item["quantity"],
            item["symbol"],
            float(item["price"]),
            float(item["fee"]),
            float(item["stamp_duty"]),
            str(item["notes"]),
            str(item["id"]),
        )

    def __compute_total(self):
        if self.action in (
            Actions.DEPOSIT,
            Actions.WITHDRAW,
            Actions.DIVIDEND,
            Actions.FEE,
        ):
            return self.quantity
        elif self.action == Actions.BUY:
            cost = (self.price / 100) * self.quantity
            total = cost + self.fee + ((cost * self.sdr) / 100)
            return total * -1
        elif self.action == Actions.SELL:
            cost = (self.price / 100) * self.quantity
            total = cost + self.fee + ((cost * self.sdr) / 100)
            return total
        return 0

    def _create_id(self):
        return hashlib.sha1(str(time.time()).encode("utf-8")).hexdigest()
