import pytest

from tradingmate.model import Holding


def test_init():
    holding = Holding("mock", 10)
    assert holding.get_symbol() == "mock"
    assert holding.get_quantity() == 10
    assert holding.get_open_price() is None
    assert holding.get_last_price() is None
    assert holding.get_last_price_valid() is False

    holding = Holding("mock", 10, 100)
    assert holding.get_symbol() == "mock"
    assert holding.get_quantity() == 10
    assert holding.get_open_price() == 100
    assert holding.get_last_price() is None
    assert holding.get_last_price_valid() is False


def test_init_fail():
    with pytest.raises(ValueError):
        _ = Holding("mock", -1)
    with pytest.raises(ValueError):
        _ = Holding("mock", 0)
    with pytest.raises(ValueError):
        _ = Holding("mock", 1, -1)


def test_get_cost():
    h = Holding("mock", 100)
    assert h.get_cost() is None

    h = Holding("mock", 100, 100)
    assert h.get_cost() == 100  # £

    h.set_open_price(1)
    assert h.get_cost() == 1  # £

    h.set_open_price(0)
    assert h.get_cost() == 0  # £


def test_get_value():
    h = Holding("mock", 100)
    assert h.get_value() is None

    h = Holding("mock", 100, 100)
    h.set_last_price(50)
    assert h.get_value() == 50  # £

    h.set_last_price(1)
    assert h.get_value() == 1  # £

    h.set_last_price(0)
    assert h.get_value() == 0  # £


def test_get_profit_loss():
    h = Holding("mock", 1, 100)
    assert h.get_profit_loss() is None

    h.set_last_price(500)
    assert h.get_profit_loss() == 4  # £

    h.set_last_price(1)
    assert h.get_profit_loss() == -0.99


def test_get_profit_loss_perc():
    h = Holding("mock", 1, 100)
    assert h.get_profit_loss_perc() is None

    h.set_last_price(500)
    assert h.get_profit_loss_perc() == 400

    h.set_last_price(1)
    assert h.get_profit_loss_perc() == -99


def test_set_last_price():
    h = Holding("mock", 1, 100)
    with pytest.raises(ValueError):
        h.set_last_price(-1)


def test_set_open_price():
    h = Holding("mock", 1, 100)
    with pytest.raises(ValueError):
        h.set_open_price(-1)


def test_set_quantity():
    h = Holding("mock", 1, 100)
    with pytest.raises(ValueError):
        h.set_quantity(-1)
    with pytest.raises(ValueError):
        h.set_quantity(0)


def test_set_last_price_invalid():
    h = Holding("mock", 1, 100)
    h.set_last_price(1000)
    assert h.get_last_price_valid()
    h.set_last_price_invalid()
    assert h.get_last_price_valid() is False
