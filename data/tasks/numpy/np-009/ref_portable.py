import numpy as np


def growth_path(factors):
    return np.cumprod(np.asarray(factors))
