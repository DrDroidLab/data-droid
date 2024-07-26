import time


def current_milli_time():
    return round(time.time() * 1000)


def current_epoch():
    return int(time.time())
