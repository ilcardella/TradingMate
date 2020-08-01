Modules
#######

Each section of this document provides the source code documentation of each
component of TradingMate.


TradingMate
===========

.. automodule:: tradingmate

.. autoclass:: TradingMate
    :members:

Model
=====

The ``model`` module contains the business logic and the data management of
TradingMate.

.. automodule:: tradingmate.model

Holding
-------

.. autoclass:: Holding
    :members:

Portfolio
---------

.. autoclass:: Portfolio
    :members:

DatabaseHandler
---------------

.. autoclass:: DatabaseHandler
    :members:

StockPriceGetter
----------------

.. autoclass:: StockPriceGetter
    :members:

ConfigurationManager
--------------------

.. autoclass:: ConfigurationManager
    :members:

Trade
-----

.. autoclass:: Trade
    :members:

Broker
======

The ``broker`` module contains the interfaces to connect to the online market brokers

.. automodule:: tradingmate.model.broker

AlphaVantageInterface
---------------------

.. autoclass:: AlphaVantageInterface
    :members:

YFinanceInterface
-----------------

.. autoclass:: YFinanceInterface
    :members:

StocksInterface
---------------

.. autoclass:: StocksInterface
    :members:

StocksInterfaceFactory
----------------------

.. autoclass:: StocksInterfaceFactory
    :members:

UI
===

The ``ui`` module contains the components that compose the User Interface
of TradingMate.

.. automodule:: tradingmate.ui

DataInterface
-------------

.. autoclass:: DataInterface
    :members:

TradingMateClient
-----------------

.. autoclass:: TradingMateClient
    :members:

GTK
---

The ``gtk`` module contains the gtk components and widgets of the
graphical interface. They are not documented due to a Sphinx issue when
importing the ``gi`` Python module

Utils
=====

The ``utils`` module contains all the utlity components.

.. automodule:: tradingmate.utils

Enums
-----

.. autoclass:: Actions
    :members:

.. autoclass:: Markets
    :members:

.. autoclass:: Messages
    :members:

TaskThread
----------

.. autoclass:: TaskThread
    :members:

Utils
-----

.. autoclass:: Utils
    :members:
