# TradingMate
[![Build Status](https://travis-ci.com/ilcardella/TradingMate.svg?branch=master)](https://travis-ci.com/ilcardella/TradingMate) [![Documentation Status](https://readthedocs.org/projects/tradingmate/badge/?version=latest)](https://tradingmate.readthedocs.io/en/latest/?badge=latest)

TradingMate is a portfolio manager for stocks traders. It lets you record all
your trades with a simple and basic interface, showing the current status of
your assets and the overall profit (or loss!)

## Dependencies

- Python 3.6+
- Poetry (only for development)
- PyGObject: https://pygobject.readthedocs.io/en/latest/index.html
- AlphaVantage: https://www.alphavantage.co/
- YFinance: https://github.com/ranaroussi/yfinance

View `pyproject.toml` for the full list of python dependencies.

## Install

First install python 3
```
sudo apt-get update
sudo apt-get install python3
```

The UI is based on Python GTK+ 3 so follow the instructions provided [here](https://pygobject.readthedocs.io/en/latest/getting_started.html) to install the required packages.

Install `TradingMate` by running the following command in the repository root folder
```
make install-system
```

## Setup

TradingMate support different sources to fetch stocks prices. The desired interface can be configured through a configuration parameter as explained below and based on the chosen interface you can follow the related setup instructions.

### AlphaVantage

AlphaVantage is great collection of API that provide several feature. It requires a key:

- Visit AlphaVantage website: `https://www.alphavantage.co`
- Request a free api key
- Insert these info in a file called `.credentials` in `${HOME}/.TradingMate/data`
    ```
    touch ${HOME}/.TradingMate/data/.credentials
    ```

    This must be in json format and contain:
    ```
    {
        "av_api_key": "key_from_alphavantage"
    }
    ```

- Revoke permissions to read the file by others

    ```
    sudo chmod 600 ${HOME}/.TradingMate/data/.credentials
    ```

### YFinance

YFinance uses Yahoo Finance REST API and it does not require authentication

### Configuration file

The `config.json` file is in the `${HOME}/.TradingMate/config` folder and it contains several parameters to personalise how TradingMate works.
These are the descriptions of each parameter:

- **trading_logs**: The absolute path of the trading logs to automatically load on startup
- **general**
  - **credentials_filepath**: File path of the .credentials file
  - **polling_period_sec**: Period of time in seconds for stock prices polling
  - **stocks_interface**
    - **active**: The active API used to retrieve stock data
    - **values**: Supported values
- **alpha_vantage**
  - **api_base_uri**: Base URI of AlphaVantage API
  - **polling_period_sec**: The period of time (in seconds) between each AlphaVantage query
- **yfinance**
  - **polling_period_sec**: The period of time (in seconds) between each query

## Start TradingMate

You can start TradingMate with
```
trading_mate
```

## Uninstall
You can use `pip` to uninstall `TradingMate`:
```
sudo pip3 uninstall TradingMate
```

## Development

Install `poetry` on your system: https://python-poetry.org/

Create the virtual environment with poetry
```
cd /path/to/repository
make install
```

### Test

You can run the test from the workspace with:
```
make test
```

### Documentation

The Sphinx documentation contains further details about each TradingMate module.
Read the documentation at:

https://tradingmate.readthedocs.io

You can build it locally from the repo root folder:
```
make docs
```

The generated html files will be under `docs/_build/html`.

## Contributing

Any contribution or suggestion is welcome, please follow the suggested workflow.

### Pull Requests

To add a new feature or to resolve a bug, create a feature branch from the
`master` branch.

Commit your changes and if possible add unit/integration test cases.
Eventually push your branch and create a Pull Request against `master`.

If you instead find problems or you have ideas and suggestions for future
improvements, please open an Issue. Thanks for the support!

Python GTK+ 3 reference: [here](https://lazka.github.io/pgi-docs/index.html#Gtk-3.0)
