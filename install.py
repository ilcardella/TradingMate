#!/usr/bin/env python3

import os
import shutil
import time

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
HOME_DIR = os.path.expanduser("~")
TRADINGMATE_DIR = "{}/.TradingMate".format(HOME_DIR)
LOG_DIR = "{}/log".format(TRADINGMATE_DIR)
DATA_DIR = "{}/data".format(TRADINGMATE_DIR)
CONFIG_DIR = "{}/config".format(TRADINGMATE_DIR)
INSTALL_DIR = "/opt/TradingMate"
CONFIG_FILE = "{}/config.json".format(CONFIG_DIR)

def install():
    print("Installing TradingMate...")
    # If installation dir exists, then clean everything
    if os.path.exists(INSTALL_DIR):
        shutil.rmtree(INSTALL_DIR)
    # Copy all sources
    print('Creating installation folder {}'.format(INSTALL_DIR))
    shutil.copytree(
        os.path.join(SCRIPT_DIR, "src"),
        os.path.join(INSTALL_DIR, "src"),
        ignore=shutil.ignore_patterns("*.pc"),
    )
    # Create TradingMate user folder
    print('Creating user folders in {}'.format(TRADINGMATE_DIR))
    os.makedirs(TRADINGMATE_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    # Backup existing configuration and copy new default configuration
    if os.path.exists(CONFIG_FILE):
        print('Backing up existing configuration file...')
        os.rename(
            CONFIG_FILE, os.path.join(CONFIG_DIR, "config_{}.json".format(time.time()))
        )
    shutil.copy(os.path.join(SCRIPT_DIR, "config", "config.json"), CONFIG_DIR)

    print("Installation complete")
    print(
        "IMPORTANT: change ownership of the following folder: {}".format(TRADINGMATE_DIR)
    )
    print("Use the following command: sudo chown -R $USER: {}".format(TRADINGMATE_DIR))


def check_root_user():
    """
    Check if the current user is root and exit if not
    """
    if not os.geteuid() == 0:
        print("This script must be run as root!")
        exit(1)


if __name__ == "__main__":
    check_root_user()
    install()
