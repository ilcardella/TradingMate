# Source: http://code.activestate.com/recipes/65222-run-a-task-every-few-seconds/

import threading
import time


class TaskThread(threading.Thread):
    """Thread that executes a task every N seconds"""

    _timeout: threading.Event
    _finished: threading.Event
    _enabled: threading.Event
    _interval: float = 1
    _singleRun: bool = False
    _start_delay: float = 0

    def __init__(self) -> None:
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._timeout = threading.Event()
        self._finished = threading.Event()
        self._enabled = threading.Event()
        self._enabled.set()
        self._interval = 1  # default value
        self._singleRun = False
        self._start_delay = 0

    def setInterval(self, interval: float) -> None:
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval

    def shutdown(self) -> None:
        """Stop this thread"""
        self._timeout.set()
        self._enabled.set()
        self._finished.set()

    def enable(self, enabled: bool) -> None:
        """Disable/enable this thread"""
        self._enabled.set() if enabled else self._enabled.clear()

    def is_enabled(self) -> bool:
        return self._enabled.is_set()

    def cancel_timeout(self):
        """Cancel the timeout and run the task"""
        self._timeout.set()

    def force_single_run(self) -> None:
        self._singleRun = True
        self.enable(True)
        self.cancel_timeout()

    def run(self) -> None:
        time.sleep(self._start_delay)
        while 1:
            # reset timeout
            self._timeout.clear()
            # check shutdown flag
            if self._finished.is_set():
                return
            # sleep until enabled or return immediatly
            self._enabled.wait()
            # perform task
            self.task()
            # Check if it was a single run
            if self._singleRun:
                self.enable(False)
            self._singleRun = False
            # sleep for interval or until shutdown
            self._timeout.wait(self._interval)

    def task(self) -> None:
        """The task done by this thread - override in subclasses"""
        raise NotImplementedError(
            "TaskThread: task function not overridden by children class!"
        )

    def start_delayed(self, delay_s: float) -> None:
        self._start_delay = delay_s
        self.start()
