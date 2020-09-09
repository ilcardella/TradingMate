import logging
from typing import Optional


class Holding:
    """Represent a current open position for a Market"""

    _symbol: str
    _quantity: int
    _open_price: Optional[float] = None
    _last_price: Optional[float] = None
    _last_price_valid: bool = False

    def __init__(
        self, symbol: str, quantity: int, open_price: Optional[float] = None
    ) -> None:
        if quantity is None or quantity < 1:
            logging.error("Holding - init: Invalid quantity")
            raise ValueError("Invalid quantity")
        if open_price is not None and open_price < 0:
            logging.error("Holding - init: Invalid open_price")
            raise ValueError("Invalid open_price")
        self._symbol = symbol
        self._quantity = quantity
        self._open_price = open_price
        self._last_price = None
        self._last_price_valid = False

    def set_last_price(self, price: float) -> None:
        if price is None or price < 0:
            logging.error("Holding - set_last_price: Invalid price")
            raise ValueError("Invalid price")
        self._last_price = price
        self._last_price_valid = True

    def set_open_price(self, price: float) -> None:
        if price is None or price < 0:
            logging.error("Holding - set_open_price: Invalid price")
            raise ValueError("Invalid price")
        self._open_price = price

    def set_quantity(self, value: int) -> None:
        if value is None or value < 1:
            logging.error("Holding - set_quantity: Invalid quantity")
            raise ValueError("Invalid quantity")
        self._quantity = value

    def add_quantity(self, value: int) -> None:
        """
        Add or subtract (if value is negative) the value to the holding quantity
        """
        self._quantity += value

    def set_last_price_invalid(self) -> None:
        self._last_price_valid = False

    def get_symbol(self) -> str:
        return self._symbol

    def get_last_price(self) -> Optional[float]:
        return self._last_price

    def get_open_price(self) -> Optional[float]:
        return self._open_price

    def get_quantity(self) -> int:
        return self._quantity

    def get_cost(self) -> Optional[float]:
        if self._open_price is None:
            return None
        return self._quantity * (self._open_price / 100)  # £

    def get_value(self) -> Optional[float]:
        if self._last_price is None:
            return None
        return self._quantity * (self._last_price / 100)  # £

    def get_profit_loss(self) -> Optional[float]:
        value = self.get_value()
        cost = self.get_cost()
        if value is None or cost is None:
            return None
        return value - cost

    def get_profit_loss_perc(self) -> Optional[float]:
        pl = self.get_profit_loss()
        cost = self.get_cost()
        if pl is None or cost is None:
            return None
        return (pl / cost) * 100

    def get_last_price_valid(self) -> bool:
        return self._last_price_valid
