import datetime
import hashlib
import logging
import time

from tradingmate.utils.Utils import Actions

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT


class Trade:
    def __init__(self, date, action, quantity, symbol, price, fee, sdr, notes, id=None):
        try:
            self.date = date
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
            "date": self.date.strftime(DATETIME_FORMAT),
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
            datetime.datetime.strptime(item["date"], DATETIME_FORMAT),
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
