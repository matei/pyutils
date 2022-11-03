from print_utils import *
from time import sleep


def wait_until(condition, sleep_period: 10, max_cycles: 80):
    """
    Wait until callable
    :param condition:
    :param sleep_period:
    :param max_cycles:
    :return:
    """
    current_cycle = 0
    while current_cycle < max_cycles:
        current_cycle += 1
        print_status(f'Cycle {current_cycle}/{max_cycles}')
        if condition():
            return True
        sleep(sleep_period)
    return False
