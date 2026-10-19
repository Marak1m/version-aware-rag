import numpy as np


def step_sizes(a):
    return np.diff(np.asarray(a))
