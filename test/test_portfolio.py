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
from Utils.ConfigurationManager import ConfigurationManager
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
    # Use test configuration file
    config = ConfigurationManager('test/test_data/config.json')
    return Portfolio(config, config.get_trading_database_path()[0])

def test_stop(portfolio):
    portfolio.stop()
    assert True

def test_get_name(portfolio):
    # name read from the test trading_log.json
    assert portfolio.get_name() == 'mock1'

def test_get_cash_available(portfolio):
    assert portfolio.get_cash_available() == 2379.3144236000016

def test_get_cash_deposited(portfolio):
    assert portfolio.get_cash_deposited() == 7700

def test_get_holding_list(portfolio):
    assert len(portfolio.get_holding_list()) == 2
    assert portfolio.get_holding_list()[0]._symbol == 'MOCK13'
    assert portfolio.get_holding_list()[1]._symbol == 'MOCK4'

def test_get_holding_symbol(portfolio):
    assert len(portfolio.get_holding_symbols()) == 2
    assert portfolio.get_holding_symbols()[0] == 'MOCK13'
    assert portfolio.get_holding_symbols()[1] == 'MOCK4'

def test_get_holding_quantity(portfolio):
    assert portfolio.get_holding_quantity('MOCK13') == 1192
    assert portfolio.get_holding_quantity('MOCK4') == 438

# def test_get_holding_last_price(portfolio, trades):
#     portfolio.start(trades)

#     with pytest.raises(ValueError) as e:
#         assert portfolio.get_holding_last_price('MOCK') is None

#     assert portfolio.get_holding_last_price('MOCK13') == 105.6700
#     assert portfolio.get_holding_last_price('MOCK4') == 105.6700

def test_get_holding_open_price(portfolio):
    with pytest.raises(ValueError) as e:
        assert portfolio.get_holding_open_price('MOCK') is None
    assert portfolio.get_holding_open_price('MOCK13') == 166.984
    assert portfolio.get_holding_open_price('MOCK4') == 582.9117

# def test_get_total_value(portfolio, trades):
#     assert portfolio.get_total_value() == 0
#     portfolio.start(trades)

#     assert portfolio.get_total_value() == 0

def test_clear(portfolio):
    portfolio.clear()
    assert portfolio.get_cash_available() == 0
    assert portfolio.get_cash_deposited() == 0
    assert len(portfolio.get_holding_list()) == 0

def test_reload(portfolio):
    test_clear(portfolio)
    portfolio.reload()
    assert portfolio.get_cash_available() == 2379.3144236000016
    assert portfolio.get_cash_deposited() == 7700
    assert len(portfolio.get_holding_list()) == 2
    assert len(portfolio.get_holding_symbols()) == 2
    assert portfolio.get_holding_symbols()[0] == 'MOCK13'
    assert portfolio.get_holding_symbols()[1] == 'MOCK4'
    assert portfolio.get_holding_quantity('MOCK13') == 1192
    assert portfolio.get_holding_quantity('MOCK4') == 438

def test_compute_avg_holding_open_price(portfolio, trades):
    price = portfolio.compute_avg_holding_open_price('MOCK13', trades)
    assert price == 166.984
    price = portfolio.compute_avg_holding_open_price('MOCK4', trades)
    assert price == 582.9117
    price = portfolio.compute_avg_holding_open_price('MOCK', trades)
    assert price is None

def test_is_trade_valid(portfolio):
    # Valid buy
    item = {'date':'01/01/0001','action':'BUY','quantity':1,'symbol':'MOCK','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid sell
    item = {'date':'01/01/0001','action':'SELL','quantity':1,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid deposit
    item = {'date':'01/01/0001','action':'DEPOSIT','quantity':1000,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid withdraw
    item = {'date':'01/01/0001','action':'WITHDRAW','quantity':2000,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid dividend
    item = {'date':'01/01/0001','action':'DIVIDEND','quantity':1123,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    assert portfolio.is_trade_valid(Trade.from_dict(item))
    # Valid fee
    item = {'date':'01/01/0001','action':'FEE','quantity':1123,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    assert portfolio.is_trade_valid(Trade.from_dict(item))

    # Invalid buy
    item = {'date':'01/01/0001','action':'BUY','quantity':1000,'symbol':'MOCK','price':1000.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    with pytest.raises(RuntimeError):
        assert not portfolio.is_trade_valid(Trade.from_dict(item))
    # Invalid sell
    item = {'date':'01/01/0001','action':'SELL','quantity':1990,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    with pytest.raises(RuntimeError):
        assert not portfolio.is_trade_valid(Trade.from_dict(item))
    # Invalid withdraw
    item = {'date':'01/01/0001','action':'WITHDRAW','quantity':20000,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    with pytest.raises(RuntimeError):
        assert not portfolio.is_trade_valid(Trade.from_dict(item))
    # Invalid fee
    item = {'date':'01/01/0001','action':'FEE','quantity':20000,'symbol':'MOCK13','price':1.0,'fee':1.0,'stamp_duty':1.0,'notes':'mock'}
    with pytest.raises(RuntimeError):
        assert not portfolio.is_trade_valid(Trade.from_dict(item))
