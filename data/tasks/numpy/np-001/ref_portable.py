import numpy as np


def area_under(y, x):
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    return float(np.sum((x[1:] - x[:-1]) * (y[1:] + y[:-1]) / 2.0))
