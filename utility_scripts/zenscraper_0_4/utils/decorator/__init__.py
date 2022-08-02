""" utils.decorator v_0_1 - add decorator functions"""
from threading import Thread
from ..logger import logger


def threaded(func):
    """
    Decorator that multithreads the target function
    with the given parameters. Returns the thread
    created for the function
    """
    logger.info('This function is Threaded')

    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args)
        thread.start()
        return thread

    return wrapper