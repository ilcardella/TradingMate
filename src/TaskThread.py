# Source: http://code.activestate.com/recipes/65222-run-a-task-every-few-seconds/

import threading


class TaskThread(threading.Thread):
    """Thread that executes a task every N seconds"""
    
    def __init__(self, updatePeriod):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = updatePeriod
    
    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval
    
    def shutdown(self):
        """Stop this thread"""
        self._finished.set()
    
    def run(self):
        while 1:
            if self._finished.isSet(): return
            self.task()
            
            # sleep for interval or until shutdown
            self._finished.wait(self._interval)
    
    def task(self):
        """The task done by this thread - override in subclasses"""
        raise Exception("TaskThread: task function not overridden by children class!")
