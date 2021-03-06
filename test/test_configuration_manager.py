from pathlib import Path

import pytest

from tradingmate.model import ConfigurationManager


@pytest.fixture
def cm():
    return ConfigurationManager(Path("test/test_data/config.json"))


def test_config_values(cm):
    config = cm.get_trading_database_path()
    assert isinstance(config, list)
    assert len(config) == 3
    assert config[0] == Path("test/test_data/trading_log.json")
    assert config[1] == Path("test/test_data/trading_log.json")
    assert config[2] == Path("test/test_data/trading_log.json")

    config = cm.get_credentials_path()
    assert isinstance(config, Path)
    assert config == Path("test/test_data/.credentials")

    config = cm.get_polling_period()
    assert isinstance(config, float)
    assert config >= 0.0

    config = cm.get_configured_stocks_interface()
    assert isinstance(config, str)
    assert config in ["yfinance", "alpha_vantage"]

    config = cm.get_alpha_vantage_api_key()
    assert isinstance(config, str)
    assert config == "API_KEY"

    config = cm.get_alpha_vantage_base_url()
    assert isinstance(config, str)
    assert config == "https://www.alphavantage.co/query"

    config = cm.get_alpha_vantage_polling_period()
    assert isinstance(config, float)
    assert config >= 0.0

    config = cm.get_yfinance_polling_period()
    assert isinstance(config, float)
    assert config >= 0.0

    config = cm.get_editable_config()
    assert isinstance(config, dict)
    assert len(config) > 0

    # Do not test save_settings() to not overwrite the test config.json
