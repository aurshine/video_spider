import time
import random


def delay(seconds):
    time.sleep(seconds)


def random_delay(minimum, maximum):
    """
    随机延迟
    """
    delay(random.uniform(minimum, maximum))


class Delay:
    """
    延迟装饰器
    """
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            random_delay(self.minimum, self.maximum)
            return func(*args, **kwargs)

        return wrapper