import json
import os
import time
from pathlib import Path

import pytest

from tradingmate.model import ConfigurationManager, Portfolio, Trade

# These variables are based on the content of the test trading log
PF_CASH_AVAILABLE = 2465.0343736000013
PF_CASH_DEPOSITED = 7700
PF_MOCK13_QUANTITY = 1192
PF_MOCK4_QUANTITY = 438
PF_MOCK13_LAST_PRICE = 1245.01904296875
PF_MOCK4_LAST_PRICE = 1245.01904296875
PF_MOCK13_OPEN_PRICE = 166.984
PF_MOCK4_OPEN_PRICE = 582.9117
PF_TOTAL_VALUE = 22758.844773990626
PF_HOLDINGS_VALUE = 20293.810400390626
PF_PL = 15058.844773990626
PF_PL_PERC = 195.56941264922892
PF_POSITIONS_PL = 15750.207874390626
PF_POSITIONS_PL_PERC = 346.6458120899158


def read_json(filepath, symbol):
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            # data["Meta Data"]["2. Symbol"] = symbol
            return data
    except IOError:
        exit()


def wait_for_prices(portfolio):
    while portfolio.get_holding_last_price("MOCK13") is None:
        time.sleep(0.1)
    while portfolio.get_holding_last_price("MOCK4") is None:
        time.sleep(0.1)


@pytest.fixture
def portfolio(requests_mock):
    # Mock http calls for mock symbols
    URL_13 = "https://query1.finance.yahoo.com/v8/finance/chart/MOCK13?range=1d&interval=1h&includePrePost=False&events=div%2Csplits"
    URL_4 = "https://query1.finance.yahoo.com/v8/finance/chart/MOCK4?range=1d&interval=1h&includePrePost=False&events=div%2Csplits"
    data_13 = read_json("test/test_data/mock_yf_1d_1h.json", "MOCK13")
    data_4 = read_json("test/test_data/mock_yf_1d_1h.json", "MOCK4")
    requests_mock.get(URL_13, status_code=200, json=data_13)
    requests_mock.get(URL_4, status_code=200, json=data_4)
    # Use test configuration file
    config = ConfigurationManager(Path("test/test_data/config.json"))
    return Portfolio(config, config.get_trading_database_path()[0])


def test_stop(portfolio):
    portfolio.stop()
    assert True


def test_get_name(portfolio):
    assert portfolio.get_name() == "mock1"


def test_get_cash_available(portfolio):
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE


def test_get_cash_deposited(portfolio):
    assert portfolio.get_cash_deposited() == PF_CASH_DEPOSITED


def test_get_holding_list(portfolio):
    assert len(portfolio.get_holding_list()) == 2
    assert portfolio.get_holding_list()[0]._symbol == "MOCK13"
    assert portfolio.get_holding_list()[1]._symbol == "MOCK4"


def test_get_holding_symbol(portfolio):
    assert len(portfolio.get_holding_symbols()) == 2
    assert portfolio.get_holding_symbols()[0] == "MOCK13"
    assert portfolio.get_holding_symbols()[1] == "MOCK4"


def test_get_holding_quantity(portfolio):
    assert portfolio.get_holding_quantity("MOCK13") == PF_MOCK13_QUANTITY
    assert portfolio.get_holding_quantity("MOCK4") == PF_MOCK4_QUANTITY


def test_get_holding_last_price(portfolio):
    wait_for_prices(portfolio)
    with pytest.raises(ValueError):
        assert portfolio.get_holding_last_price("MOCK") is None
    assert portfolio.get_holding_last_price("MOCK13") == PF_MOCK13_LAST_PRICE
    assert portfolio.get_holding_last_price("MOCK4") == PF_MOCK4_LAST_PRICE


def test_get_holding_open_price(portfolio):
    with pytest.raises(ValueError):
        assert portfolio.get_holding_open_price("MOCK") is None
    assert portfolio.get_holding_open_price("MOCK13") == PF_MOCK13_OPEN_PRICE
    assert portfolio.get_holding_open_price("MOCK4") == PF_MOCK4_OPEN_PRICE


def test_get_total_value(portfolio):
    assert portfolio.get_total_value() is None
    wait_for_prices(portfolio)
    assert portfolio.get_total_value() == PF_TOTAL_VALUE


def test_get_holdings_value(portfolio):
    assert portfolio.get_holdings_value() is None
    wait_for_prices(portfolio)
    assert portfolio.get_holdings_value() == PF_HOLDINGS_VALUE


def test_get_portfolio_pl(portfolio):
    assert portfolio.get_portfolio_pl() is None
    wait_for_prices(portfolio)
    assert portfolio.get_portfolio_pl() == PF_PL


def test_get_portfolio_pl_perc(portfolio):
    assert portfolio.get_portfolio_pl_perc() is None
    wait_for_prices(portfolio)
    assert portfolio.get_portfolio_pl_perc() == PF_PL_PERC


def test_get_open_positions_pl(portfolio):
    assert portfolio.get_open_positions_pl() is None
    wait_for_prices(portfolio)
    assert portfolio.get_open_positions_pl() == PF_POSITIONS_PL


def test_get_open_positions_pl_perc(portfolio):
    assert portfolio.get_open_positions_pl_perc() is None
    wait_for_prices(portfolio)
    assert portfolio.get_open_positions_pl_perc() == PF_POSITIONS_PL_PERC


def test_has_unsaved_changes(portfolio):
    assert portfolio.has_unsaved_changes() is False
    item = {
        "id": "0",
        "date": "01/01/0001 00:00",
        "action": "DEPOSIT",
        "quantity": 1000,
        "symbol": "",
        "price": 0,
        "fee": 0,
        "stamp_duty": 0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.has_unsaved_changes() is True
    portfolio.save_portfolio("/tmp/TradingMate_test_portfolio.json")
    assert portfolio.has_unsaved_changes() is False


def test_get_trade_history(portfolio):
    assert len(portfolio.get_trade_history()) == 54
    assert all(map(lambda t: isinstance(t, Trade), portfolio.get_trade_history()))


def test_save_portfolio(portfolio):
    filepath = Path("/tmp/TradingMate_test_save_portfolio.json")
    if filepath.exists():
        os.remove(filepath)
    assert not filepath.exists()
    portfolio.save_portfolio(filepath)
    assert filepath.exists()
    config = ConfigurationManager(Path("test/test_data/config.json"))
    new_pf = Portfolio(config, filepath)
    test_get_total_value(new_pf)


def test_add_trade(portfolio):
    # NOTE The dates in the mock items below needs to be sequencial
    # Valid buy
    item = {
        "id": "0",
        "date": "01/01/2020 00:00",
        "action": "BUY",
        "quantity": 1,
        "symbol": "MOCK",
        "price": 1.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_holding_quantity("MOCK") == 1
    # Valid sell
    item = {
        "id": "0",
        "date": "02/01/2020 00:00",
        "action": "SELL",
        "quantity": 1,
        "symbol": "MOCK",
        "price": 1.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_holding_quantity("MOCK") == 0
    # Valid deposit
    item = {
        "id": "0",
        "date": "03/01/2020 00:00",
        "action": "DEPOSIT",
        "quantity": 1000,
        "symbol": "",
        "price": 0,
        "fee": 0,
        "stamp_duty": 0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE + 1000
    # Valid withdraw
    item = {
        "id": "0",
        "date": "04/01/2020 00:00",
        "action": "WITHDRAW",
        "quantity": 1000,
        "symbol": "",
        "price": 0.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE
    # Withdraws should not affect cash deposited
    assert portfolio.get_cash_deposited() == PF_CASH_DEPOSITED
    # Valid dividend
    item = {
        "id": "0",
        "date": "05/01/2020 00:00",
        "action": "DIVIDEND",
        "quantity": 1,
        "symbol": "MOCK13",
        "price": 0.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE + 1
    # Dividends should not affect cash deposited
    assert portfolio.get_cash_deposited() == PF_CASH_DEPOSITED
    # Valid fee
    item = {
        "id": "0",
        "date": "06/01/2020 00:00",
        "action": "FEE",
        "quantity": 1,
        "symbol": "",
        "price": 0.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE


def test_add_trade_past_date(portfolio):
    # NOTE The dates in the mock items below needs to be sequencial
    # Valid buy
    item = {
        "id": "0",
        "date": "01/09/2018 00:00",
        "action": "BUY",
        "quantity": 1,
        "symbol": "MOCK",
        "price": 1.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_holding_quantity("MOCK") == 1
    # Valid sell
    item = {
        "id": "0",
        "date": "02/09/2018 00:00",
        "action": "SELL",
        "quantity": 1,
        "symbol": "MOCK",
        "price": 1.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_holding_quantity("MOCK") == 0
    # Valid deposit
    item = {
        "id": "0",
        "date": "03/09/2018 00:00",
        "action": "DEPOSIT",
        "quantity": 1000,
        "symbol": "",
        "price": 0,
        "fee": 0,
        "stamp_duty": 0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE + 1000
    # Valid withdraw
    item = {
        "id": "0",
        "date": "04/09/2018 00:00",
        "action": "WITHDRAW",
        "quantity": 1000,
        "symbol": "",
        "price": 0.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE
    # Withdraws should not affect cash deposited
    assert portfolio.get_cash_deposited() == PF_CASH_DEPOSITED
    # Valid dividend
    item = {
        "id": "0",
        "date": "05/09/2018 00:00",
        "action": "DIVIDEND",
        "quantity": 1,
        "symbol": "MOCK13",
        "price": 0.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE + 1
    # Dividends should not affect cash deposited
    assert portfolio.get_cash_deposited() == PF_CASH_DEPOSITED
    # Valid fee
    item = {
        "id": "0",
        "date": "06/09/2018 00:00",
        "action": "FEE",
        "quantity": 1,
        "symbol": "",
        "price": 0.0,
        "fee": 0.0,
        "stamp_duty": 0.0,
        "notes": "mock",
    }
    portfolio.add_trade(Trade.from_dict(item))
    assert portfolio.get_cash_available() == PF_CASH_AVAILABLE


def test_add_trade_invalid(portfolio):
    # Invalid buy due to too high cost
    item = {
        "id": "0",
        "date": "01/01/2020 00:00",
        "action": "BUY",
        "quantity": 1000,
        "symbol": "MOCK",
        "price": 1000.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "mock",
    }
    with pytest.raises(RuntimeError):
        portfolio.add_trade(Trade.from_dict(item))
    # Invalid sell
    item = {
        "id": "0",
        "date": "02/01/2020 00:00",
        "action": "SELL",
        "quantity": 1990,
        "symbol": "MOCK13",
        "price": 1.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "mock",
    }
    with pytest.raises(RuntimeError):
        portfolio.add_trade(Trade.from_dict(item))
    # Invalid withdraw
    item = {
        "id": "0",
        "date": "03/01/2020 00:00",
        "action": "WITHDRAW",
        "quantity": 20000,
        "symbol": "MOCK13",
        "price": 1.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "mock",
    }
    with pytest.raises(RuntimeError):
        assert not portfolio.add_trade(Trade.from_dict(item))
    # Invalid fee
    item = {
        "id": "0",
        "date": "04/01/2020 00:00",
        "action": "FEE",
        "quantity": 20000,
        "symbol": "MOCK13",
        "price": 1.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "mock",
    }
    with pytest.raises(RuntimeError):
        assert not portfolio.add_trade(Trade.from_dict(item))


def test_add_trade_invalid_past_date(portfolio):
    # Invalid buy due to too high cost
    item = {
        "id": "0",
        "date": "01/01/2018 00:00",
        "action": "BUY",
        "quantity": 1000,
        "symbol": "MOCK",
        "price": 1000.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "mock",
    }
    with pytest.raises(RuntimeError):
        portfolio.add_trade(Trade.from_dict(item))
    # Invalid sell
    item = {
        "id": "0",
        "date": "02/01/2018 00:00",
        "action": "SELL",
        "quantity": 1990,
        "symbol": "MOCK13",
        "price": 1.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "mock",
    }
    with pytest.raises(RuntimeError):
        portfolio.add_trade(Trade.from_dict(item))
    # Invalid withdraw
    item = {
        "id": "0",
        "date": "03/01/2018 00:00",
        "action": "WITHDRAW",
        "quantity": 20000,
        "symbol": "MOCK13",
        "price": 1.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "mock",
    }
    with pytest.raises(RuntimeError):
        assert not portfolio.add_trade(Trade.from_dict(item))
    # Invalid fee
    item = {
        "id": "0",
        "date": "04/01/2018 00:00",
        "action": "FEE",
        "quantity": 20000,
        "symbol": "MOCK13",
        "price": 1.0,
        "fee": 1.0,
        "stamp_duty": 1.0,
        "notes": "mock",
    }
    with pytest.raises(RuntimeError):
        assert not portfolio.add_trade(Trade.from_dict(item))
