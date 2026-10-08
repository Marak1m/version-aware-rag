import numpy as np


def running_total(a):
    return np.cumsum(np.asarray(a))
