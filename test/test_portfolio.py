import os
import sys
import inspect
import pytest

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, '{}/src'.format(parentdir))

from Model.Portfolio import Portfolio

@pytest.fixture
def portfolio():
    p = Portfolio('mock')
    return p

def test_set_cash_available(portfolio):
    portfolio.set_cash_available(1000)

    with pytest.raises(ValueError) as e:
        portfolio.set_cash_available(-1)

def test_set_invested_amount(portfolio):
    portfolio.set_invested_amount(100)
    with pytest.raises(ValueError) as e:
        portfolio.set_invested_amount(-1)

def test_update_holding_amount(portfolio):
    assert portfolio.get_holding_amount('mock') == 0
    portfolio.update_holding_amount('mock', 100)
    assert portfolio.get_holding_amount('mock') == 100
    portfolio.update_holding_amount('mock', 100)
    assert portfolio.get_holding_amount('mock') == 100
    portfolio.update_holding_amount('mock', 0)
    assert portfolio.get_holding_amount('mock') == 0
    with pytest.raises(ValueError) as e:
        portfolio.update_holding_amount('mock', -1)

def test_update_holding_last_price(portfolio):
    with pytest.raises(ValueError) as e:
        portfolio.get_holding_last_price('mock')
    with pytest.raises(ValueError) as e:
        portfolio.update_holding_last_price('mock', 100)
    portfolio.update_holding_amount('mock', 100)
    with pytest.raises(ValueError) as e:
        portfolio.update_holding_last_price('mock', -1)
    portfolio.update_holding_last_price('mock', 1000)
    assert portfolio.get_holding_last_price('mock') == 1000

def test_update_holding_open_price(portfolio):
    with pytest.raises(ValueError) as e:
        portfolio.get_holding_open_price('mock')
    with pytest.raises(ValueError) as e:
        portfolio.update_holding_open_price('mock', 100)
    portfolio.update_holding_amount('mock', 100)
    with pytest.raises(ValueError) as e:
        portfolio.update_holding_open_price('mock', -1)
    portfolio.update_holding_open_price('mock', 1000)
    assert portfolio.get_holding_open_price('mock') == 1000

def test_clear(portfolio):
    portfolio.set_cash_available(1000)
    portfolio.set_invested_amount(1000)
    portfolio.update_holding_amount('mock', 100)
    portfolio.update_holding_last_price('mock', 1000)
    assert portfolio.get_cash_available() == 1000
    assert portfolio.get_invested_amount() == 1000
    assert portfolio.get_holdings_value() == 1000
    assert len(portfolio.get_holding_list()) == 1
    portfolio.clear()
    assert portfolio.get_cash_available() == 0
    assert portfolio.get_invested_amount() == 0
    assert portfolio.get_holdings_value() == 0
    assert len(portfolio.get_holding_list()) == 0

def test_get_name(portfolio):
    assert portfolio.get_name() == 'mock'

def test_get_cash_available(portfolio):
    assert portfolio.get_cash_available() == 0
    portfolio.set_cash_available(1000)
    assert portfolio.get_cash_available() == 1000

def test_get_invested_amount(portfolio):
    assert portfolio.get_invested_amount() == 0
    portfolio.set_invested_amount(1000)
    assert portfolio.get_invested_amount() == 1000

def test_get_holding_list(portfolio):
    assert len(portfolio.get_holding_list()) == 0
    portfolio.update_holding_amount('mock1', 100)
    portfolio.update_holding_amount('mock2', 200)
    assert len(portfolio.get_holding_list()) == 2
    holding = portfolio.get_holding_list()[0]
    assert holding.get_symbol() == 'mock1'
    assert holding.get_amount() == 100
    holding = portfolio.get_holding_list()[1]
    assert holding.get_symbol() == 'mock2'
    assert holding.get_amount() == 200

def test_get_holding_symbols(portfolio):
    assert len(portfolio.get_holding_symbols()) == 0
    portfolio.update_holding_amount('mock1', 100)
    portfolio.update_holding_amount('mock2', 200)
    assert len(portfolio.get_holding_symbols()) == 2
    assert portfolio.get_holding_symbols()[0] == 'mock1'
    assert portfolio.get_holding_symbols()[1] == 'mock2'

# TODO not testing the "holding" related functions as plan to change this

def test_get_total_value(portfolio):
    assert portfolio.get_total_value() == 0
    portfolio.set_cash_available(1000)
    portfolio.update_holding_amount('mock1', 100)
    assert portfolio.get_total_value() is None
    portfolio.update_holding_last_price('mock1', 1000)
    assert portfolio.get_total_value() == 2000

def test_get_holdings_value(portfolio):
    assert portfolio.get_holdings_value() == 0
    portfolio.update_holding_amount('mock1', 100)
    assert portfolio.get_holdings_value() is None
    portfolio.update_holding_last_price('mock1', 500)
    assert portfolio.get_holdings_value() == 500
    portfolio.update_holding_amount('mock2', 1000)
    assert portfolio.get_holdings_value() is None
    portfolio.update_holding_last_price('mock2', 1)
    assert portfolio.get_holdings_value() == 510

def test_get_portfolio_pl(portfolio):
    assert portfolio.get_portfolio_pl() == 0
    portfolio.update_holding_amount('mock1', 1000)
    assert portfolio.get_portfolio_pl() is None
    portfolio.update_holding_open_price('mock1', 100)
    assert portfolio.get_portfolio_pl() is None
    portfolio.update_holding_last_price('mock1', 200)
    assert portfolio.get_portfolio_pl() == 2000
    portfolio.set_invested_amount(1)
    assert portfolio.get_portfolio_pl() == 1999
    portfolio.update_holding_amount('mock2', 100)
    assert portfolio.get_portfolio_pl() is None
    portfolio.update_holding_open_price('mock2', 100)
    assert portfolio.get_portfolio_pl() is None
    portfolio.update_holding_last_price('mock2', 1)
    assert portfolio.get_portfolio_pl() == 2000
    portfolio.set_cash_available(1000)
    assert portfolio.get_portfolio_pl() == 3000
    portfolio.set_invested_amount(1000)
    assert portfolio.get_portfolio_pl() == 2001

def test_get_portfolio_pl_perc(portfolio):
    assert portfolio.get_portfolio_pl_perc() is None
    portfolio.update_holding_amount('mock1', 1000)
    assert portfolio.get_portfolio_pl_perc() is None
    portfolio.update_holding_open_price('mock1', 100)
    assert portfolio.get_portfolio_pl_perc() is None
    portfolio.update_holding_last_price('mock1', 200)
    assert portfolio.get_portfolio_pl_perc() is None
    portfolio.set_invested_amount(1)
    expected = float(((2000 - 1) / 1) * 100)
    assert portfolio.get_portfolio_pl_perc() == expected

    portfolio.update_holding_amount('mock2', 100)
    assert portfolio.get_portfolio_pl_perc() is None
    portfolio.update_holding_open_price('mock2', 100)
    assert portfolio.get_portfolio_pl_perc() is None
    portfolio.update_holding_last_price('mock2', 1)
    expected = float(((2001 - 1) / 1) * 100)
    assert portfolio.get_portfolio_pl_perc() == expected
    portfolio.set_cash_available(1000)
    expected = float(((3001 - 1) / 1) * 100)
    assert portfolio.get_portfolio_pl_perc() == expected
    portfolio.set_invested_amount(1900)
    expected = float(((3001 - 1900) / 1900) * 100)
    assert portfolio.get_portfolio_pl_perc() == expected

def test_get_open_positions_pl(portfolio):
    assert portfolio.get_open_positions_pl() == 0
    portfolio.update_holding_amount('mock1', 1000)
    assert portfolio.get_open_positions_pl() is None
    portfolio.update_holding_open_price('mock1', 100)
    assert portfolio.get_open_positions_pl() is None
    portfolio.update_holding_last_price('mock1', 200)
    assert portfolio.get_open_positions_pl() == 1000

    portfolio.update_holding_amount('mock2', 100)
    assert portfolio.get_open_positions_pl() is None
    portfolio.update_holding_open_price('mock2', 100)
    assert portfolio.get_open_positions_pl() is None
    portfolio.update_holding_last_price('mock2', 1)
    assert portfolio.get_open_positions_pl() == 901

def test_get_open_positions_pl_perc(portfolio):
    assert portfolio.get_open_positions_pl_perc() is None
    portfolio.update_holding_amount('mock1', 1000)
    assert portfolio.get_open_positions_pl_perc() is None
    portfolio.update_holding_open_price('mock1', 100)
    assert portfolio.get_open_positions_pl_perc() is None
    portfolio.update_holding_last_price('mock1', 200)
    assert portfolio.get_open_positions_pl_perc() == 100

    portfolio.update_holding_amount('mock2', 100)
    assert portfolio.get_open_positions_pl_perc() is None
    portfolio.update_holding_open_price('mock2', 100)
    assert portfolio.get_open_positions_pl_perc() is None
    portfolio.update_holding_last_price('mock2', 1)
    expected = float(((2001 - 1100) / 1100) * 100) # value - cost / cost * 100
    assert portfolio.get_open_positions_pl_perc() == expected
