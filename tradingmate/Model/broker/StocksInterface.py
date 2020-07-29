import functools
import inspect
import os
import sys
import threading

# Mutex used for thread synchronisation
lock = threading.Lock()


def synchronised(lock):
    """ Thread synchronization decorator """

    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)

        return inner_wrapper

    return wrapper


class Singleton(type):
    """Metaclass to implement the Singleton desing pattern"""

    _instances = {}

    @synchronised(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class StocksInterface(metaclass=Singleton):
    def get_last_close_price(self, market_id):
        raise NotImplementedError("Must implement get_last_close_price")
