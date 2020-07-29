import os

import pytest

from tradingmate.Model.DatabaseHandler import DatabaseHandler
from tradingmate.Utils.ConfigurationManager import ConfigurationManager
from tradingmate.Utils.Trade import Trade


@pytest.fixture
def configuration():
    return ConfigurationManager("test/test_data/config.json")


@pytest.fixture
def dbh(configuration):
    return DatabaseHandler(configuration, "test/test_data/trading_log.json")


def test_read_data(dbh):
    """
    Test read data from json file
    """
    assert len(dbh.trading_history) > 0
    dbh.trading_history = []
    assert len(dbh.trading_history) == 0
    dbh.read_data("test/test_data/trading_log.json")
    assert len(dbh.trading_history) > 0


def test_write_data(dbh):
    """
    Test write data into json file
    """
    mock_path = "/tmp/test.json"
    if os.path.exists(mock_path):
        os.remove(mock_path)
    assert not os.path.isfile(mock_path)
    assert dbh.write_data(mock_path)
    assert os.path.isfile(mock_path)


def test_get_db_filepath(dbh):
    """
    Test it returns the correct filepath
    """
    assert dbh.get_db_filepath() == "test/test_data/trading_log.json"

    mock_path = "/tmp/test.json"
    assert dbh.write_data(mock_path)
    assert os.path.isfile(mock_path)
    dbh.read_data(mock_path)
    assert dbh.get_db_filepath() == mock_path


def test_get_trades_list(dbh):
    """
    Test it returns the list of trades read from the json file
    """
    trades = dbh.get_trades_list()
    assert len(trades) > 0


def test_add_trade(dbh):
    """
    Test it adds the trade to the in memory list
    """
    prev_len = len(dbh.trading_history)
    item = {
        "id": "0",
        "date": "01/01/0001 00:00",
        "action": "BUY",
        "quantity": 1,
        "symbol": "MOCK",
        "price": 1.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "hello",
    }
    trade = Trade.from_dict(item)
    dbh.add_trade(trade)
    assert len(dbh.trading_history) == prev_len + 1


def test_delete_trade(dbh):
    """
    Test it removes the trade from the in memory list
    """
    prev_len = len(dbh.trading_history)
    item = {
        "id": "42",
        "date": "01/01/0001 00:00",
        "action": "BUY",
        "quantity": 1,
        "symbol": "MOCK",
        "price": 1.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "hello",
    }
    trade = Trade.from_dict(item)
    dbh.add_trade(trade)
    assert len(dbh.trading_history) == prev_len + 1
    dbh.delete_trade("42")
    assert len(dbh.trading_history) == prev_len


def test_get_trading_log_name(dbh):
    """Test the db name is read"""
    assert dbh.get_trading_log_name() == "mock1"
