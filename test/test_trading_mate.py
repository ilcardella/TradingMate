import json
import os
import re

import pytest

from tradingmate import TradingMate
from tradingmate.model import Portfolio, Trade


def read_json(filepath):
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data
    except IOError:
        exit()


@pytest.fixture
def trading_mate(requests_mock):
    # Mock http calls for mock symbols in the test portfolio
    URL_YF_MOCK13 = "https://query1.finance.yahoo.com/v8/finance/chart/MOCK13"
    URL_YF_MOCK4 = "https://query1.finance.yahoo.com/v8/finance/chart/MOCK4"
    URL_YF_MOCK = "https://query1.finance.yahoo.com/v8/finance/chart/MOCK"
    data_MOCK13 = read_json("test/test_data/mock_yf_1d_1h.json")
    data_MOCK4 = data_MOCK13
    data_MOCK = data_MOCK4
    requests_mock.get(re.compile(URL_YF_MOCK13), status_code=200, json=data_MOCK13)
    requests_mock.get(re.compile(URL_YF_MOCK4), status_code=200, json=data_MOCK4)
    requests_mock.get(re.compile(URL_YF_MOCK), status_code=200, json=data_MOCK)
    # Mock HTML data for MOCK used in the tests below
    URL_YF_HTML_MOCK = "https://finance.yahoo.com/quote/MOCK"
    with open("test/test_data/mock_yf_quote.html", "r") as f:
        requests_mock.get(URL_YF_HTML_MOCK, status_code=200, body=f)
    # Create the TradingMate instance using the test config file
    return TradingMate("test/test_data/config.json", "/tmp/trading_mate_test_log.log")


def test_get_portfolios(trading_mate):
    pfs = trading_mate.get_portfolios()
    assert len(pfs) == 3
    assert isinstance(pfs[0], Portfolio)
    assert isinstance(pfs[1], Portfolio)
    assert isinstance(pfs[2], Portfolio)


def test_close_view_event(trading_mate):
    trading_mate.close_view_event()
    assert True


def test_manual_refresh_event(trading_mate):
    for pf in trading_mate.get_portfolios():
        trading_mate.manual_refresh_event(pf.get_id())
        # TODO assert that a http get is done
    assert True


def test_set_auto_refresh(trading_mate):
    for pf in trading_mate.get_portfolios():
        trading_mate.set_auto_refresh(False, pf.get_id())
        # TODO assert no http get are done
        trading_mate.set_auto_refresh(True, pf.get_id())
        # TODO assert http get is done
    assert True


def test_new_trade_event(trading_mate):
    trade_dict = {
        "id": "new_trade",
        "date": "01/01/2020 00:00",
        "action": "DEPOSIT",
        "quantity": 1000,
        "symbol": "MSFT",
        "price": 1000,
        "fee": 10,
        "stamp_duty": 0.5,
        "notes": "some notes",
    }
    for pf in trading_mate.get_portfolios():
        trade = Trade.from_dict(trade_dict)
        trading_mate.new_trade_event(trade, pf.get_id())
    # Verify the trade has been added
    for pf in trading_mate.get_portfolios():
        assert pf.get_trade_history()[-1].id == "new_trade"
    # Verify invalid trade is rejected
    invalid_trade = {
        "id": "mock",
        "date": "01/01/2020 00:00",
        "action": "BUY",
        "quantity": 10000,
        "symbol": "MSFT",
        "price": 100000,
        "fee": 10,
        "stamp_duty": 0.5,
        "notes": "some notes",
    }
    for pf in trading_mate.get_portfolios():
        trade = Trade.from_dict(invalid_trade)
        with pytest.raises(RuntimeError) as e:
            trading_mate.new_trade_event(trade, pf.get_id())


def test_delete_trade_event(trading_mate):
    for pf in trading_mate.get_portfolios():
        # Disable auto refresh so we do not need to mock requests for MOCK1
        trading_mate.set_auto_refresh(False, pf.get_id())
        with pytest.raises(RuntimeError) as e:
            trading_mate.delete_trade_event(pf.get_id(), "mock_initial_deposit")
        trading_mate.delete_trade_event(pf.get_id(), "mock_last_trade")
    # Verify the last trade has been deleted
    for pf in trading_mate.get_portfolios():
        assert pf.get_trade_history()[-1].id != "mock_last_trade"


def test_open_portfolio_event(trading_mate):
    assert len(trading_mate.get_portfolios()) == 3
    with pytest.raises(Exception) as e:
        trading_mate.open_portfolio_event("/tmp/non_existing_file.json")
    trading_mate.open_portfolio_event("test/test_data/trading_log.json")
    assert len(trading_mate.get_portfolios()) == 4


def test_save_portfolio_event(trading_mate):
    for pf in trading_mate.get_portfolios():
        temp_file = f"/tmp/new_trading_log{pf.get_id()}.json"
        assert os.path.exists(temp_file) == False
        trading_mate.save_portfolio_event(pf.get_id(), temp_file)
        assert os.path.exists(temp_file)


# def test_get_settings_event(trading_mate):
#     # TODO
#     assert True

# def test_save_settings_event(trading_mate):
#     # TODO
#     assert True


def test_get_app_log_filepath(trading_mate):
    assert trading_mate.get_app_log_filepath() == "/tmp/trading_mate_test_log.log"


# This is commented out because this function depends on pip being installed
# Could be done patching subprocess.Popen call returning a mock pip response

# def test_get_app_version(trading_mate):
#     # TODO
#     assert True

# This is commented out beacuse I can't find a way to mock the http response
# Yfinance uses pandas which uses lxml to parse the html returned by urllib.request.urlopen

# def test_get_market_details(trading_mate):
#     # TODO
#     with mock.patch("urllib.request.urlopen") as mock_urllib:
#         with open("test/test_data/mock_yf_quote_holders.html", "r") as f:
#             mock_urllib.return_value.__enter__.return_value.read.return_value = f.read()
#             mock_urllib.return_value.__enter__.return_value.getcode.return_value = 200
#             details = trading_mate.get_market_details("MOCK")
#             assert details is not None
