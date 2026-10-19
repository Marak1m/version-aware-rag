import numpy as np


def step_sizes(a):
    a = np.asarray(a)
    return a[:-1] - a[1:]
