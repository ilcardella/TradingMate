# TradingMate
[![Build Status](https://travis-ci.com/ilcardella/TradingMate.svg?branch=master)](https://travis-ci.com/ilcardella/TradingMate) [![Documentation Status](https://readthedocs.org/projects/tradingmate/badge/?version=latest)](https://tradingmate.readthedocs.io/en/latest/?badge=latest)

TradingMate is a portfolio manager for stocks traders. It lets you record all
your trades with a simple and basic interface, showing the current status of
your assets and the overall profit (or loss!)

# Dependencies

- Python 3.5+
- Pipenv
- Tkinter: https://docs.python.org/3/library/tk.html
- AlphaVantage: https://www.alphavantage.co/

View `Pipfile` for the full list of python dependencies.

# Install

First install python 3 and pipenv
```
sudo apt-get update && sudo apt-get install python3 python3-pip
sudo -H pip3 install -U pipenv
```

The UI is based on Tkinter so let's install it
```
sudo apt-get update && sudo apt-get install python3-tk
```

Clone this repo in your workspace and setup the python virtual environment
by running the following commands in the repository root folder
```
pipenv install
```
You can install development packages adding the flag `--dev`

After that, to install TradingMate simply run:
```
./install.py
```

All necessary files will be copied in `/$HOME/.TradingMate/bin` by default.
It is recommended to add this path to your `PATH` environment variable.

# Setup

TradingMate uses AlphaVantage to fetch markets data online:

- Visit AlphaVantage website: `https://www.alphavantage.co`
- Request a free api key
- Insert these info in a file called `.credentials` in `$HOME/.TradingMate/data`
```
touch $HOME/.TradingMate/data/.credentials
```

This must be in json format and contain:
```
{
    "av_api_key": "apiKey"
}
```

- Revoke permissions to read the file by others

```
cd $HOME/.TradingMate/data
sudo chmod 600 .credentials
```
### Configuration file

The `config.json` file is in the `$HOME/.TradingMate/config` folder and it contains several parameters to personalise how TradingMate works.
These are the descriptions of each parameter:

- **general/trading_log_path**: The absolute path of the trading log where the history of your trades are saved
- **general/credentials_filepath**: File path of the .credentials file
- **alpha_vantage/api_base_uri**: Base URI of AlphaVantage API
- **alpha_vantage/polling_period_sec**: The polling period to query AlphaVantage for stock prices

# Start TradingMate

You can start TradingMate in your current terminal
```
$HOME/.TradingMate/bin/TradingMate.py
```
or you can start it in detached mode, letting it run in the background
```
nohup /opt/TradingMate/src/TradingMate.py >/dev/null 2>&1 &
```

# Stop TradingMate

To stop a TradingMate instance running in the background
```
ps -ef | grep TradingMate | xargs kill -9
```

# Test

You can run the test from the workspace with:
```
pipenv run pytest
```

NOTE: you must have installed the python dependencies with the `--dev` flag

# Documentation

The Sphinx documentation contains further details about each TradingMate module
with source code documentation of each component.

Read the documentation at:

https://tradingmate.readthedocs.io

You can build it locally from the "workspace" root folder:
```
pipenv run sphinx-build -nWT -b html doc doc/_build/html
```

The generated html files will be under `doc/_build/html`.

# Contributing

Any contribution or suggestion is welcome, please follow the suggested workflow.

### Pull Requests

To add a new feature or to resolve a bug, create a feature branch from the
`develop` branch.

Commit your changes and if possible add unit/integration test cases.
Eventually push your branch and create a Pull Request against `develop`.

If you instead find problems or you have ideas and suggestions for future
improvements, please open an Issue. Thanks for the support!
