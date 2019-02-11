import os
import sys
import inspect
import pytest
import requests_mock
import json
import time

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, '{}/src'.format(parentdir))

from Model.Portfolio import Portfolio
from common.MockConfigurationManager import MockConfigurationManager
from Utils.Utils import Callbacks
from Utils.Trade import Trade

def mock_callback():
    pass

def read_json(filepath, symbol):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            data['Meta Data']['2. Symbol'] = symbol
            return data
    except IOError:
        exit()

@pytest.fixture
def trades():
    trades = []
    with open('test/test_data/trading_log.json', 'r') as file:
        json_obj = json.load(file)
    for item in json_obj['trades']:
        trades.append(Trade.from_dict(item))
    return trades

@pytest.fixture
def portfolio(requests_mock):
    # Mock http calls for mock symbols
    URL_13 = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MOCK13&apikey=MOCK'
    URL_4 = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MOCK14&apikey=MOCK'
    data_13 = read_json('test/test_data/mock_av_daily.json', 'MOCK13')
    data_4 = read_json('test/test_data/mock_av_daily.json', 'MOCK4')
    requests_mock.get(URL_13, status_code=200, json=data_13)
    requests_mock.get(URL_4, status_code=200, json=data_4)

    config = MockConfigurationManager()
    p = Portfolio('mock', config)
    p.set_callback(Callbacks.UPDATE_LIVE_PRICES, mock_callback)
    return p

def test_start_stop(portfolio):
    portfolio.start([])
    portfolio.stop()
    assert True

def test_get_name(portfolio):
    assert portfolio.get_name() == 'mock'

def test_get_cash_available(portfolio, trades):
    assert portfolio.get_cash_available() == 0

    portfolio.start([])
    assert portfolio.get_cash_available() == 0

    portfolio.reload(trades)
    assert portfolio.get_cash_available() == 2379.3144236000016

def test_get_invested_amount(portfolio, trades):
    assert portfolio.get_invested_amount() == 0

    portfolio.start([])
    assert portfolio.get_invested_amount() == 0

    portfolio.reload(trades)
    assert portfolio.get_invested_amount() == 7700

def test_get_holding_list(portfolio, trades):
    assert len(portfolio.get_holding_list()) == 0

    portfolio.start([])
    assert len(portfolio.get_holding_list()) == 0

    portfolio.reload(trades)
    assert len(portfolio.get_holding_list()) == 2
    assert portfolio.get_holding_list()[0]._symbol == 'MOCK13'
    assert portfolio.get_holding_list()[1]._symbol == 'MOCK4'

def test_get_holding_symbol(portfolio, trades):
    assert len(portfolio.get_holding_symbols()) == 0

    portfolio.start([])
    assert len(portfolio.get_holding_symbols()) == 0

    portfolio.reload(trades)
    assert len(portfolio.get_holding_symbols()) == 2
    assert portfolio.get_holding_symbols()[0] == 'MOCK13'
    assert portfolio.get_holding_symbols()[1] == 'MOCK4'

def test_get_holding_quantity(portfolio, trades):
    portfolio.start(trades)

    assert portfolio.get_holding_quantity('MOCK13') == 1192
    assert portfolio.get_holding_quantity('MOCK4') == 438

# def test_get_holding_last_price(portfolio, trades):
#     portfolio.start(trades)

#     with pytest.raises(ValueError) as e:
#         assert portfolio.get_holding_last_price('MOCK') is None

#     assert portfolio.get_holding_last_price('MOCK13') == 105.6700
#     assert portfolio.get_holding_last_price('MOCK4') == 105.6700

def test_get_holding_open_price(portfolio, trades):
    portfolio.start(trades)

    with pytest.raises(ValueError) as e:
        assert portfolio.get_holding_open_price('MOCK') is None

    assert portfolio.get_holding_open_price('MOCK13') == 166.984
    assert portfolio.get_holding_open_price('MOCK4') == 582.9117

# def test_get_total_value(portfolio, trades):
#     assert portfolio.get_total_value() == 0
#     portfolio.start(trades)

#     assert portfolio.get_total_value() == 0

def test_clear(portfolio, trades):
    portfolio.start(trades)
    portfolio.clear()
    assert portfolio.get_cash_available() == 0
    assert portfolio.get_invested_amount() == 0
    assert len(portfolio.get_holding_list()) == 0

def test_reload(portfolio, trades):
    portfolio.start(trades)
    portfolio.clear()
    portfolio.reload(trades)
    assert portfolio.get_cash_available() == 2379.3144236000016
    assert portfolio.get_invested_amount() == 7700
    assert len(portfolio.get_holding_list()) == 2
    assert len(portfolio.get_holding_symbols()) == 2
    assert portfolio.get_holding_symbols()[0] == 'MOCK13'
    assert portfolio.get_holding_symbols()[1] == 'MOCK4'
    assert portfolio.get_holding_quantity('MOCK13') == 1192
    assert portfolio.get_holding_quantity('MOCK4') == 438

def test_compute_avg_holding_open_price(portfolio, trades):
    portfolio.start(trades)
    price = portfolio.compute_avg_holding_open_price('MOCK13', trades)
    assert price == 166.984
    price = portfolio.compute_avg_holding_open_price('MOCK4', trades)
    assert price == 582.9117
    price = portfolio.compute_avg_holding_open_price('MOCK', trades)
    assert price is None

def test_is_trade_valid(portfolio, trades):
    portfolio.start(trades)

    # Valid buy
    item = {'date':'01/01/0001','action':'BUY','quantity':1,'symbol':'MOCK','price':1.0,'fee':1.0,'stamp_duty':1.0}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid sell
    item = {'date':'01/01/0001','action':'SELL','quantity':1,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid deposit
    item = {'date':'01/01/0001','action':'DEPOSIT','quantity':1000,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid withdraw
    item = {'date':'01/01/0001','action':'WITHDRAW','quantity':2000,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid dividend
    item = {'date':'01/01/0001','action':'DIVIDEND','quantity':1123,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0}
    assert portfolio.is_trade_valid(Trade.from_dict(item))

    # Invalid buy
    item = {'date':'01/01/0001','action':'BUY','quantity':1000,'symbol':'MOCK','price':1000.0,'fee':1.0,'stamp_duty':1.0}
    with pytest.raises(RuntimeError):
        assert not portfolio.is_trade_valid(Trade.from_dict(item))
    # Invalid sell
    item = {'date':'01/01/0001','action':'SELL','quantity':1990,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0}
    with pytest.raises(RuntimeError):
        assert not portfolio.is_trade_valid(Trade.from_dict(item))
    # Invalid withdraw
    item = {'date':'01/01/0001','action':'WITHDRAW','quantity':20000,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0}
    with pytest.raises(RuntimeError):
        assert not portfolio.is_trade_valid(Trade.from_dict(item))
