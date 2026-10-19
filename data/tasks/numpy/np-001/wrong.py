import numpy as np


def area_under(y, x):
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    return float(np.sum(y[:-1] * np.diff(x)))
