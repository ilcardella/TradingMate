import hashlib
import logging
import time
from datetime import datetime
from typing import Dict, Union

from ..utils import Actions

TIME_FORMAT: str = "%H:%M"
DATE_FORMAT: str = "%d/%m/%Y"
DATETIME_FORMAT: str = f"{DATE_FORMAT} {TIME_FORMAT}"

TradeDict = Dict[str, Union[str, float, int]]


class Trade:
    """Represent a trade action
    """

    date: datetime
    action: Actions
    quantity: int
    symbol: str
    price: float
    fee: float
    sdr: float
    notes: str
    id: str

    def __init__(
        self,
        date: datetime,
        action: Actions,
        quantity: int,
        symbol: str,
        price: float,
        fee: float,
        sdr: float,
        notes: str,
        id: str = None,
    ) -> None:
        try:
            self.date = date
            if type(action) is not Actions:
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

    def to_dict(self) -> TradeDict:
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

    def to_string(self) -> str:
        return (
            f"{self.date}_{self.action.name}_{self.quantity}_{self.symbol}_{self.price}"
        )

    @staticmethod
    def from_dict(item: TradeDict) -> "Trade":
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
            datetime.strptime(str(item["date"]), DATETIME_FORMAT),
            Actions[str(item["action"])],
            int(item["quantity"]),
            str(item["symbol"]),
            float(item["price"]),
            float(item["fee"]),
            float(item["stamp_duty"]),
            str(item["notes"]),
            str(item["id"]),
        )

    def __compute_total(self) -> float:
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
        return 0.0

    def _create_id(self) -> str:
        return hashlib.sha1(str(time.time()).encode("utf-8")).hexdigest()
