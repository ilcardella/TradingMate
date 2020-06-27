Modules
=======

Each section of this document provides the source code documentation of each
component of TradingMate.


TradingMate
-----------

.. automodule:: TradingMate

.. autoclass:: TradingMate
    :members:

Model
-----

The ``Model`` module contains the business logic and the data management of
TradingMate.


Holding
^^^^^^^

.. automodule:: Model.Holding

.. autoclass:: Holding
    :members:

Portfolio
^^^^^^^^^

.. automodule:: Model.Portfolio

.. autoclass:: Portfolio
    :members:

DatabaseHandler
^^^^^^^^^^^^^^^

.. automodule:: Model.DatabaseHandler

.. autoclass:: DatabaseHandler
    :members:

StockPriceGetter
^^^^^^^^^^^^^^^^

.. automodule:: Model.StockPriceGetter

.. autoclass:: StockPriceGetter
    :members:

UI
---

The ``UI`` module contains the components that compose the User Interface
of TradingMate.

DataInterface
^^^^^^^^^^^^^

.. automodule:: UI.DataInterface

.. autoclass:: DataInterface
    :members:

TradingMateClient
^^^^^^^^^^^^^^^^^

.. automodule:: UI.TradingMateClient

.. autoclass:: TradingMateClient
    :members:

GTK
^^^

The ``gtk`` module contains the gtk components and widgets of the
graphical interface. They are not documented due to a Sphinx issue when
importing the ``gi`` Python module

Utils
-----

The ``Utils`` module contains all the utlity components.


ConfigurationManager
^^^^^^^^^^^^^^^^^^^^

.. automodule:: Utils.ConfigurationManager

.. autoclass:: ConfigurationManager
    :members:

TaskThread
^^^^^^^^^^

.. automodule:: Utils.TaskThread

.. autoclass:: TaskThread
    :members:

Trade
^^^^^

.. automodule:: Utils.Trade

.. autoclass:: Trade
    :members:

Utils
^^^^^

.. automodule:: Utils.Utils

.. autoclass:: Actions
    :members:

.. autoclass:: Messages
    :members:

.. autoclass:: Markets
    :members:
