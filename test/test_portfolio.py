import os
import sys
import inspect
import pytest

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, '{}/src'.format(parentdir))

from Model.Portfolio import Portfolio
from common.MockConfigurationManager import MockConfigurationManager
from Utils.Utils import Callbacks

def mock_callback():
    pass

@pytest.fixture
def portfolio():
    config = MockConfigurationManager()
    p = Portfolio('mock', config)
    p.set_callback(Callbacks.UPDATE_LIVE_PRICES, mock_callback)
    p.start([])
    return p

def test(portfolio):
    assert True
