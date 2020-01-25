# TradingMate
[![Build Status](https://travis-ci.com/ilcardella/TradingMate.svg?branch=master)](https://travis-ci.com/ilcardella/TradingMate) [![Documentation Status](https://readthedocs.org/projects/tradingmate/badge/?version=latest)](https://tradingmate.readthedocs.io/en/latest/?badge=latest)

TradingMate is a portfolio manager for stocks traders. It lets you record all
your trades with a simple and basic interface, showing the current status of
your assets and the overall profit (or loss!)

## Dependencies

- Python 3.6+
- Pipenv (only for development)
- PyGObject: https://pygobject.readthedocs.io/en/latest/index.html
- AlphaVantage: https://www.alphavantage.co/

View `Pipfile` or `setup.py` for the full list of python dependencies.

## Install

First install python 3
```
sudo apt-get update
sudo apt-get install python3
```

The UI is based on Python GTK+ 3 so follow the instructions provided [here](https://pygobject.readthedocs.io/en/latest/getting_started.html) to install the required packages.

Clone this repo in your workspace and install `TradingMate` by running the following command in the repository root folder
```
sudo python3 setup.py install
```

## Setup

TradingMate uses AlphaVantage to fetch markets data online:

- Visit AlphaVantage website: `https://www.alphavantage.co`
- Request a free api key
- Insert these info in a file called `.credentials` in `/opt/TradingMate/data`
    ```
    touch /opt/TradingMate/data/.credentials
    ```

    This must be in json format and contain:
    ```
    {
        "av_api_key": "key_from_alphavantage"
    }
    ```

- Revoke permissions to read the file by others

    ```
    sudo chmod 600 /opt/TradingMate/data/.credentials
    ```

### Configuration file

The `config.json` file is in the `/opt/TradingMate/config` folder and it contains several parameters to personalise how TradingMate works.
These are the descriptions of each parameter:

- **trading_logs**: The absolute path of the trading logs to automatically load on startup
- **general/credentials_filepath**: File path of the .credentials file
- **alpha_vantage/api_base_uri**: Base URI of AlphaVantage API
- **alpha_vantage/polling_period_sec**: The period of time (in seconds) between each AlphaVantage query for stock prices

## Start TradingMate

You can start TradingMate with
```
sudo trading_mate
```

Otherwise you can change ownership of the `/opt/TradingMate` folder:
```
sudo chown -R $USER: /opt/TradingMate
```
and then run `TradingMate` without sudo
```
trading_mate
```

## Uninstall
You can use `pip` to uninstall `TradingMate`:
```
sudo pip3 uninstall TradingMate
```

## Development

The `Pipfile` helps you to setup a development virtual environmnet installing the required dependencies.
Install `pip` and `pipenv`
```
sudo apt-get update
sudo apt-get install python3-pip
sudo -H pip3 install -U pipenv
```

Create the virtual environment
```
cd /path/to/repository
pipenv install
```

### Test

You can run the test from the workspace with:
```
pipenv run test
```

### Documentation

The Sphinx documentation contains further details about each TradingMate module.
Read the documentation at:

https://tradingmate.readthedocs.io

You can build it locally from the repo root folder:
```
pipenv run docs
```

The generated html files will be under `doc/_build/html`.

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
