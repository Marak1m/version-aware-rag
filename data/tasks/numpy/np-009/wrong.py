import numpy as np


def growth_path(factors):
    a = np.asarray(factors)
    return np.concatenate(([1], np.cumprod(a)[:-1]))
