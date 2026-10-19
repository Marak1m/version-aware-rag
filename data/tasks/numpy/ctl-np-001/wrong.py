from itertools import accumulate


def running_total(a):
    return list(accumulate(a))
