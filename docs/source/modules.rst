Modules
#######

Each section of this document provides the source code documentation of each
component of TradingMate.


TradingMate
===========

.. automodule:: TradingMate

.. autoclass:: TradingMate
    :members:

Model
=====

The ``model`` module contains the business logic and the data management of
TradingMate.


Holding
-------

.. automodule:: model.Holding

.. autoclass:: Holding
    :members:

Portfolio
---------

.. automodule:: model.Portfolio

.. autoclass:: Portfolio
    :members:

DatabaseHandler
---------------

.. automodule:: model.DatabaseHandler

.. autoclass:: DatabaseHandler
    :members:

StockPriceGetter
----------------

.. automodule:: model.StockPriceGetter

.. autoclass:: StockPriceGetter
    :members:

ConfigurationManager
--------------------

.. automodule:: model.ConfigurationManager

.. autoclass:: ConfigurationManager
    :members:

Trade
-----

.. automodule:: model.Trade

.. autoclass:: Trade
    :members:

UI
===

The ``ui`` module contains the components that compose the User Interface
of TradingMate.

DataInterface
-------------

.. automodule:: ui.DataInterface

.. autoclass:: DataInterface
    :members:

TradingMateClient
-----------------

.. automodule:: ui.TradingMateClient

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

TaskThread
----------

.. automodule:: utils.TaskThread

.. autoclass:: TaskThread
    :members:

Utils
-----

.. automodule:: utils

.. autoclass:: Actions
    :members:

.. autoclass:: Messages
    :members:

.. autoclass:: Markets
    :members:
