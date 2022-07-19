import time
from threading import Thread

class Decorator:

    logger = None

    def __init__(self, logger):
        self.logger = logger


    def retry(self, func, retry_times=3, sleep_seconds=1, false_output=None):
        """
        retry until output not equals to false_output
        :param func: input a function to retry
        :param retry_times: the number of retry
        :param sleep_seconds: sleep time
        :param false_output: output that should be disregarded on the retry
        :return: value or false_output
        """

        def retry_decorator():
            for i in range(retry_times + 1):
                if i > 0:
                    self.logger.warning('retrying a %s function %s times', func().__name__, i)
                try:
                    data = func()
                except Exception as err:  # pylint: disable=broad-except
                    self.logger.error(err)
                    time.sleep(sleep_seconds)
                    continue
                if false_output is None:
                    if data is not false_output:
                        break
                else:
                    if data != false_output:
                        break
                time.sleep(sleep_seconds)
            return data

        return retry_decorator

    @staticmethod
    def threaded(func):
        """
        Decorator that multithreads the target function
        with the given parameters. Returns the thread
        created for the function
        """

        def wrapper(*args, **kwargs):
            thread = Thread(target=func, args=args)
            thread.start()
            return thread

        return wrapper