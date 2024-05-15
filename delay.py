import time
import datetime
import random


def delay(seconds):
    time.sleep(seconds)


def random_delay(minimum, maximum):
    """
    随机延迟
    """
    assert 0 <= minimum <= maximum, '应当满足 0 <= minimum <= maximum'
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


def get_time(length: int = None):
    """
    获取长度为length的当前时间戳

    :param length:

    :return:
    """
    t = str(time.time_ns())
    if length is not None:
        if len(t) > length:
            t = t[:length]
        if len(t) < length:
            t = t.ljust(length, '0')

    return t


def get_ramdom_num(length: int = 1):
    """
    获取长度为 length的随机数字字符串

    :param length: 数字串的长度

    :return:
    """
    assert length > 0, '应当满足 length > 0'

    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def run_date(func):
    def wrapper(*args, **kwargs):
        print(datetime.datetime.now().strftime('start at: [%Y-%m-%d %H:%M:%S]'))
        func(*args, **kwargs)
        print(datetime.datetime.now().strftime('end   at: [%Y-%m-%d %H:%M:%S]'))

    return wrapper
