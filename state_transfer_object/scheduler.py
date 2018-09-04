"""
State Transfer Object Scheduler
"""
import threading
import logging

_log = logging.getLogger(__name__)


class BaseScheduler(object):
    def new_task(self, objs):
        raise NotImplementedError


class ThreadScheduler(BaseScheduler):
    def __init__(self):
        """ Load config from config file and init threads pool
        """
        self._task_name = "iterate"
        self._thread_pool = []
        self._tasks = []

    def new_task(self, objs):
        for obj in objs:
            _log.info('Create a new task for %s', obj)
            t = threading.Thread(target=self._run_task, args=(obj,))
            self._tasks.append(obj)
            self._thread_pool.append(t)
            t.start()

    def _run_task(self, obj):
        func = getattr(obj, self._task_name)
        if not func:
            raise ValueError("Cannot find function %s in %s" % (self._task_name, obj))
        func()

    def wait_all_task(self):
        for t in self._thread_pool:
            t.join()


class CoroutineScheduler(BaseScheduler):
    def __init__(self):
        pass

    def new_task(self, objs):
        pass
