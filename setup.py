from setuptools import setup, find_namespace_packages
import os

setup(
    name="TradingMate",
    version="2.0.0",
    python_requires=">=3",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    scripts=["src/TradingMate.py"],
    entry_points={"console_scripts": ["trading_mate = TradingMate:main"]},
    install_requires=["alpha-vantage==2.1.0"],
    package_data={"config": ["*.json"], "data": ["*.json"], "src/UI/assets": ["*.png"]},
    data_files=[
        (os.path.join(os.sep, "opt", "TradingMate", "config"), ["config/config.json"]),
        (os.path.join(os.sep, "opt", "TradingMate", "data"), ["data/trading_log.json"]),
        (
            os.path.join(os.sep, "opt", "TradingMate", "data", "assets"),
            [
                "src/UI/assets/trading_mate_icon.png",
                "src/UI/assets/add_icon.png",
                "src/UI/assets/open_file_icon.png",
                "src/UI/assets/save_file_icon.png",
                "src/UI/assets/save_as_file_icon.png",
            ],
        ),
        (
            os.path.join(os.sep, "opt", "TradingMate", "data", "assets", "gtk"),
            [
                "src/UI/assets/gtk/add_trade_window_layout.glade",
                "src/UI/assets/gtk/main_window_layout.glade",
                "src/UI/assets/gtk/notebook_page_layout.glade",
                "src/UI/assets/gtk/settings_window_layout.glade",
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
