from datetime import datetime

import pytest

from tradingmate.model import Trade, DATETIME_FORMAT
from tradingmate.utils import Actions


def compute_total(quantity, price, fee, sdr):
    cost = (price / 100) * quantity
    return cost + fee + ((cost * sdr) / 100)


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (Actions.BUY, compute_total(10.0, 123.456, 12.34, 0.5) * -1),
        (Actions.SELL, compute_total(10.0, 123.456, 12.34, 0.5)),
        (Actions.DEPOSIT, 10.0),
        (Actions.WITHDRAW, 10.0),
        (Actions.DIVIDEND, 10.0),
        (Actions.FEE, 10.0),
    ],
)
def test_init(test_input, expected):
    now = datetime.now()
    t = Trade(now, test_input, 10.0, "mock", 123.456, 12.34, 0.5, "notes", None)
    assert t.date == now
    assert t.action == test_input
    assert t.quantity == 10.0
    assert t.symbol == "mock"
    assert t.price == 123.456
    assert t.fee == 12.34
    assert t.sdr == 0.5
    assert t.notes == "notes"
    assert t.total == expected
    assert t.id is not None
    assert type(t.id) is str
    assert len(t.id) > 0


def test_init_fail():
    with pytest.raises(ValueError):
        _ = Trade(datetime.now(), "WRONG", 10.0, "mock", 123.456, 12.34, 0.5, "notes")


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (Actions.BUY, compute_total(10.0, 123.456, 12.34, 0.5) * -1),
        (Actions.SELL, compute_total(10.0, 123.456, 12.34, 0.5)),
        (Actions.DEPOSIT, 10.0),
        (Actions.WITHDRAW, 10.0),
        (Actions.DIVIDEND, 10.0),
        (Actions.FEE, 10.0),
    ],
)
def test_total(test_input, expected):
    t = Trade(datetime.now(), test_input, 10.0, "mock", 123.456, 12.34, 0.5, "notes")
    assert t.total == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (Actions.BUY, Actions.BUY.name),
        (Actions.SELL, Actions.SELL.name),
        (Actions.DEPOSIT, Actions.DEPOSIT.name),
        (Actions.WITHDRAW, Actions.WITHDRAW.name),
        (Actions.DIVIDEND, Actions.DIVIDEND.name),
        (Actions.FEE, Actions.FEE.name),
    ],
)
def test_to_string(test_input, expected):
    t = Trade(datetime.now(), test_input, 10.0, "mock", 123.456, 12.34, 0.5, "notes")
    assert expected in t.to_string()
    assert "10.0" in t.to_string()
    assert "mock" in t.to_string()
    assert "123.456" in t.to_string()


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (Actions.BUY, Actions.BUY.name),
        (Actions.SELL, Actions.SELL.name),
        (Actions.DEPOSIT, Actions.DEPOSIT.name),
        (Actions.WITHDRAW, Actions.WITHDRAW.name),
        (Actions.DIVIDEND, Actions.DIVIDEND.name),
        (Actions.FEE, Actions.FEE.name),
    ],
)
def test_to_dict(test_input, expected):
    now = datetime.now()
    t = Trade(now, test_input, 10.0, "mock", 123.456, 12.34, 0.5, "notes")
    assert t.to_dict() == {
        "id": t.id,
        "date": now.strftime(DATETIME_FORMAT),
        "action": expected,
        "quantity": 10.0,
        "symbol": "mock",
        "price": 123.456,
        "fee": 12.34,
        "stamp_duty": 0.5,
        "notes": "notes",
    }


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (Actions.BUY.name, Actions.BUY),
        (Actions.SELL.name, Actions.SELL),
        (Actions.DEPOSIT.name, Actions.DEPOSIT),
        (Actions.WITHDRAW.name, Actions.WITHDRAW),
        (Actions.DIVIDEND.name, Actions.DIVIDEND),
        (Actions.FEE.name, Actions.FEE),
    ],
)
def test_from_dict(test_input, expected):
    now = datetime.now().replace(second=0, microsecond=0)
    d = {
        "id": "abcdef",
        "date": now.strftime(DATETIME_FORMAT),
        "action": test_input,
        "quantity": 10.0,
        "symbol": "mock",
        "price": 123.456,
        "fee": 12.34,
        "stamp_duty": 0.5,
        "notes": "notes",
    }
    t = Trade.from_dict(d)
    assert t.id == "abcdef"
    assert t.date == now
    assert t.action == expected
    assert t.quantity == 10.0
    assert t.symbol == "mock"
    assert t.price == 123.456
    assert t.fee == 12.34
    assert t.sdr == 0.5
    assert t.notes == "notes"
