import importlib
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor


private_module = importlib.import_module('concurrent.futures.thread')


class NoWaitThreadPool(ThreadPoolExecutor):
    """
    线程池shutdown后不等待线程执行完毕以及取消未完成的任务，直接退出
    """
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=False, cancel_futures=True)
        print('exiting NoWaitThreadPool successfully')
        return False

    def _adjust_thread_count(self):
        # if idle threads are available, don't spin new threads
        if self._idle_semaphore.acquire(timeout=0):
            return

        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(None)

        num_threads = len(self._threads)
        if num_threads < self._max_workers:
            thread_name = '%s_%d' % (self._thread_name_prefix or self,
                                     num_threads)
            t = threading.Thread(name=thread_name, target=private_module._worker, daemon=True,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue,
                                       self._initializer,
                                       self._initargs))
            t.start()
            self._threads.add(t)
            private_module._threads_queues[t] = self._work_queue
