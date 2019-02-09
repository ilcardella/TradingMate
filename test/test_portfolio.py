import os
import sys
import inspect
import pytest

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, '{}/src'.format(parentdir))

from Model.Portfolio import Portfolio

class MockConfigurationManager():
    def __init__(self):
        pass

    def get_trading_database_path(self):
        return currentdir + "/test_data/trading_log.json"

    def get_alpha_vantage_api_key(self):
        return ""

    def get_alpha_vantage_base_url(self):
        return ""

    def get_alpha_vantage_polling_period(self):
        return 1

    def get_debug_log_active(self):
        return False

    def get_enable_file_log(self):
        return False

    def get_log_filepath(self):
        return ""

@pytest.fixture
def portfolio():
    config = MockConfigurationManager()
    p = Portfolio('mock', config)
    return p

def test(portfolio):
    assert True
