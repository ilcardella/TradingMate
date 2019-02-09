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

@pytest.fixture
def portfolio():
    config = MockConfigurationManager()
    p = Portfolio('mock', config)
    p.start([])
    return p

def test(portfolio):
    assert True
