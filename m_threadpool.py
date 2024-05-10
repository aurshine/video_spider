from concurrent.futures import ThreadPoolExecutor


class NoWaitThreadPool(ThreadPoolExecutor):
    """
    线程池shutdown后不等待线程执行完毕以及取消未完成的任务，直接退出
    """
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True, cancel_futures=True)
        print('exiting NoWaitThreadPool successfully')
        return False
