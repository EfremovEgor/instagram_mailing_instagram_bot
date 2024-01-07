import config
import time
import functools
import random


def sleep(function):
    @functools.wraps(function)
    def inner(*args, **kwargs):
        result = function(*args, **kwargs)
        time.sleep(
            random.randint(
                *config.PAGE_INTERACTION_INTERVAL,
            )
        )
        return result

    return inner
