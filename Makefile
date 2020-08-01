ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = >

INSTALL_DIR = ${HOME}/.TradingMate
DATA_DIR = $(INSTALL_DIR)/data
GTK_ASSETS_DIR = $(DATA_DIR)/assets/gtk
CONFIG_DIR = $(INSTALL_DIR)/config
LOG_DIR = $(INSTALL_DIR)/log

default: check

test:
> poetry run python -m pytest

docs:
> poetry run make -C docs html

install:
> poetry install -v

update:
> poetry update

remove-env:
> poetry env remove python3

install-system: clean
> pip3 install --user .
> mkdir -p $(CONFIG_DIR)
> mkdir -p $(DATA_DIR)
> mkdir -p $(GTK_ASSETS_DIR)
> mkdir -p $(LOG_DIR)
> cp config/config.json $(CONFIG_DIR)
> cp data/trading_log.json $(DATA_DIR)
> cp dtradingmate/UI/assets/gtk/*.glade $(GTK_ASSETS_DIR)

build: clean
> poetry build

mypy:
> poetry run mypy tradingmate/

flake8:
> poetry run flake8 tradingmate/ test/

isort:
> poetry run isort tradingmate/ test/

black:
> poetry run black tradingmate/ test/

format: isort black

lint: flake8 #mypy

check: format lint test

ci: install check docs build

clean:
> rm -rf *egg-info
> rm -rf build/
> rm -rf dist/
> find . -name '*.pyc' -exec rm -f {} +
> find . -name '*.pyo' -exec rm -f {} +
> find . -name '*~' -exec rm -f  {} +
> find . -name '__pycache__' -exec rm -rf  {} +
> find . -name '_build' -exec rm -rf  {} +
> find . -name '.mypy_cache' -exec rm -rf  {} +
> find . -name '.pytest_cache' -exec rm -rf  {} +

.PHONY: test lint format install docs build install-system ci check mypy flake8 isort black remove update
