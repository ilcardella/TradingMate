#!/usr/bin/env python3

import os
import shutil
import time

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
HOME_DIR = os.path.expanduser("~")
TRADINGMATE_DIR = os.path.join(HOME_DIR, ".TradingMate")
LOG_DIR = os.path.join(TRADINGMATE_DIR, "log")
DATA_DIR = os.path.join(TRADINGMATE_DIR, "data")
CONFIG_DIR = os.path.join(TRADINGMATE_DIR, "config")
INSTALL_DIR = os.path.join(TRADINGMATE_DIR, "bin")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def install():
    print("Installing TradingMate...")
    # If installation dir exists, then clean everything
    if os.path.exists(INSTALL_DIR):
        print("Cleaning installation folder {}".format(INSTALL_DIR))
        shutil.rmtree(INSTALL_DIR)
    # Copy all sources
    print("Creating installation folder {}".format(INSTALL_DIR))
    shutil.copytree(
        os.path.join(SCRIPT_DIR, "src"),
        INSTALL_DIR,
        ignore=shutil.ignore_patterns("*.pc", "__pycache__"),
    )
    # Create TradingMate user folder
    print("Creating user folders in {}".format(TRADINGMATE_DIR))
    os.makedirs(TRADINGMATE_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    # Backup existing configuration and copy new default configuration
    if os.path.exists(CONFIG_FILE):
        print("Backing up existing configuration file...")
        os.rename(
            CONFIG_FILE, os.path.join(CONFIG_DIR, "config_{}.json".format(time.time()))
        )
    shutil.copy(os.path.join(SCRIPT_DIR, "config", "config.json"), CONFIG_DIR)

    print("Installation complete")


if __name__ == "__main__":
    install()
