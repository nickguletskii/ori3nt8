import gc

from PySide2.QtCore import QObject, QThreadPool, QMutex, QRunnable


class SingleRunnableManager(QObject):
    def __init__(self, thread_pool: QThreadPool):
        """
        Runs a runnable on a thread pool, canceling the previous runnable if it is still enqueued.

        Parameters
        ----------
        thread_pool
            The thread pool that will be used to run the runnable.
        """
        super().__init__()
        self._thread_pool = thread_pool
        self._current_runnable = None
        self._lock = QMutex()

    def remove_runnable(self) -> None:
        """
        Removes the current runnable without canceling its execution.
        """
        self._lock.lock()
        try:
            del self._current_runnable
            self._current_runnable = None
            gc.collect()
        finally:
            self._lock.unlock()

    def _cancel(self) -> None:
        if self._current_runnable is not None:
            self._thread_pool.cancel(self._current_runnable)
        del self._current_runnable
        self._current_runnable = None
        gc.collect()

    def start(
            self,
            runnable: QRunnable
    ) -> None:
        """
        Cancel the current runnable (if any) and enqueue the runnable for execution on the thread pool.

        Parameters
        ----------
        runnable
            The runnable to run

        """
        self._lock.lock()
        try:
            self._cancel()
            self._thread_pool.start(runnable)
        finally:
            self._lock.unlock()
