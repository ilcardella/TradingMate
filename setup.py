from setuptools import setup, find_namespace_packages
import os

setup(
    name="TradingMate",
    version="2.2.0",
    python_requires=">=3",
    package_dir={"": "tradingmate"},
    packages=find_namespace_packages(where="tradingmate"),
    scripts=["tradingmate/TradingMate.py"],
    entry_points={"console_scripts": ["trading_mate = TradingMate:main"]},
    install_requires=[
        "alpha-vantage==2.2.0",
        "pygtail==0.11.1",
        "yfinance==0.1.54",
        "lxml==4.5.1",
    ],
    package_data={
        "config": ["*.json"],
        "data": ["*.json"],
        "tradingmate/UI/assets/gtk": ["*.glade"],
    },
    data_files=[
        (os.path.join(os.sep, "opt", "TradingMate", "config"), ["config/config.json"]),
        (os.path.join(os.sep, "opt", "TradingMate", "data"), ["data/trading_log.json"]),
        (
            os.path.join(os.sep, "opt", "TradingMate", "data", "assets", "gtk"),
            [
                "tradingmate/UI/assets/gtk/add_trade_window_layout.glade",
                "tradingmate/UI/assets/gtk/main_window_layout.glade",
                "tradingmate/UI/assets/gtk/notebook_page_layout.glade",
                "tradingmate/UI/assets/gtk/settings_window_layout.glade",
                "tradingmate/UI/assets/gtk/log_window_layout.glade",
            ],
        ),
    ],
    # metadata to display on PyPI
    author="Alberto Cardellini",
    author_email="",
    description="Portfolio manager for stocks traders",
    keywords="trading stocks finance",
    url="https://github.com/ilcardella/TradingMate",
    project_urls={
        "Bug Tracker": "https://github.com/ilcardella/TradingMate/issues",
        "Documentation": "https://tradingmate.readthedocs.io",
        "Source Code": "https://github.com/ilcardella/TradingMate",
    },
    classifiers=["License :: OSI Approved :: MIT License"],
)
