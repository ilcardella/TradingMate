import functools
import threading
from typing import Any, Dict, Optional

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


class SyncSingleton(type):
    """Metaclass to implement the Singleton desing pattern"""

    _instances: Dict[Any, Any] = {}

    @synchronised(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SyncSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class StocksInterface(metaclass=SyncSingleton):
    def get_last_close_price(self, market_id: str) -> Optional[float]:
        raise NotImplementedError("Must implement get_last_close_price")
