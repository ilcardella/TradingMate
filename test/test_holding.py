import os
import sys
import inspect
import pytest

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, '{}/src'.format(parentdir))

from Model.Holding import Holding

def test_init():
    holding = Holding('mock', 10, 100, 50)
    assert holding.get_symbol() == 'mock'
    assert holding.get_amount() == 10
    assert holding.get_open_price() == 100
    assert holding.get_last_price() == 50
