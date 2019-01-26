import os
import sys
import inspect
import pytest

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, '{}/src'.format(parentdir))

from Model.Portfolio import Portfolio

def test_init():
    p = Portfolio('mock')

def test_set_cash_available():
    p = Portfolio('mock')
    p.set_cash_available(1000)

    with pytest.raises(ValueError) as e:
        p.set_cash_available(-1)

def test_set_invested_amount():
    p = Portfolio('mock')
    p.set_invested_amount(100)
    with pytest.raises(ValueError) as e:
        p.set_invested_amount(-1)
