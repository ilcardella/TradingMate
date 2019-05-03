# TradingMate
[![Build Status](https://travis-ci.com/ilcardella/TradingMate.svg?branch=master)](https://travis-ci.com/ilcardella/TradingMate) [![Documentation Status](https://readthedocs.org/projects/tradingmate/badge/?version=latest)](https://tradingmate.readthedocs.io/en/latest/?badge=latest)

TradingMate is a portfolio manager for stocks traders. It lets you record all
your trades with a simple and basic interface, showing the current status of
your assets and the overall profit (or loss!)

# Dependencies

- Python 3.4+
- Tkinter: https://docs.python.org/3/library/tk.html
- AlphaVantage: https://www.alphavantage.co/

View file `requirements.txt` for the full list of python dependencies.

# Install

After cloning this repo, to install TradingMate simply run:
```
./trading_mate_ctrl install
```
(This will require super-user access)

The required dependencies will be installed and all necessary files installed in /opt/TradingMate by default. It is recommended to add this path to your PATH environment variable.

# Setup

TradingMate uses AlphaVantage to fetch markets data online:

- Visit AlphaVantage website: `https://www.alphavantage.co`
- Request a free api key
- Insert these info in a file called `.credentials`
This must be in json format
```
{
    "av_api_key": "apiKey"
}
```
- Copy the `.credentials` file in the `$HOME/.TradingMate/data` folder
- Revoke permissions to read the file by others
```
cd $HOME/.TradingMate/data
sudo chmod 600 .credentials
```
### Configuration file

The `config.json` file is in the `$HOME/.TradingMate/config` folder and it contains several parameters to personalise how TradingMate works.
These are the descriptions of each parameter:

- **general/trading_log_path**: The absolute path of the trading log where the history
of your trades are saved
- **general/credentials_filepath**: File path of the .credentials file
- **alpha_vantage/api_base_uri**: Base URI of AlphaVantage API
- **alpha_vantage/polling_period_sec**: The polling period to query AlphaVantage for stock prices

# Run

TradingMate can be controlled by the `trading_mate_ctrl` shell script.
The script provides commands to perform different actions:

### Start TradingMate
```
./trading_mate_ctrl start
```

### Stop TradingMate

Closing the main window will stop the whole application.
You can also use the command:
```
./trading_mate_ctrl stop
```

# Test

Test can't run with the installed script.
You can run the test from a "workspace" environment with:
```
./trading_mate_ctrl test
```
You can run the test in Docker containers against different python versions:
```
./trading_mate_ctrl test_docker
```

# Documentation

The Sphinx documentation contains further details about each TradingMate module
with source code documentation of each component.

Read the documentation at:

https://tradingmate.readthedocs.io

You can build it locally from the "workspace" root folder:
```
./trading_mate_ctrl docs
```

The generated html files will be under `doc/_build/html`.

# Contributing

I appreciate any help so if you have suggestions or issues open an Issue for discussion.
If you can contribute please just open a pull request with your changes.
Thanks for all the support!
