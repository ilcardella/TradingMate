# TradingMate

TradingMate is a portfolio manager for stocks traders. It lets you record all
your trades with a simple and basic interface, showing the current status of
your assets and the overall profit (or loss!)

# Dependencies

Python 3.4+
Tkinter: https://docs.python.org/3/library/tk.html
AlphaVantage: https://www.alphavantage.co/

View file `requirements.txt` for the full list of python dependencies.

# Setup

It is recommended to use a virtual environment to run TradingMate.

Install dependencies with pip
```
pip install -r requirements.txt
```
TradingMate supports different sources for market data, at the moment these are
the supported ones:

- AlphaVantage

It's up to you to choose your preferred one or even all of them. The following
steps depends on the what you chose:

- Visit AlphaVantage website: `https://www.alphavantage.co`
- Request a free api key
- Insert these info in a file called `.credentials`

This must be in json format

```
{
    "av_api_key": "apiKey"
}
```

- Copy the `.credentials` file in the `data` folder
- Revoke permissions to read the file if you are paranoid

```
cd data
sudo chmod 600 .credentials
```
### Configuration file

The `config.json` file is in the `config` folder and it contains several configurable parameter to personalise how TradingMate works.
These are the descriptions of each parameter:

- **trading_log_path**: The absolute path of the trading log where the history
of your trades are saved

# Run

TradingMate can be controlled by the `trading_mate_ctrl` shell script.
The script provides commands to perform different actions:

### Start TradingMate
:
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

If you have setup a virtual environment you can run the test by running `pytest`
from the project root folder.

You can run the test from a clean environment with:
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

You can build it locally from the project root folder:
```
./trading_mate_ctrl docs
```

The generated html files will be under `doc/_build/html`.

# Contributing

I am really happy to receive any help so please just open a pull request
with your changes and I will handle it.

If you instead find problems or have ideas for future improvements open an Issue. Thanks for all the support!
