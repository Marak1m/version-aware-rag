import numpy as np


def resample_linear(x_new, x, y):
    return np.interp(np.asarray(x_new, dtype=float), np.asarray(x, dtype=float), np.asarray(y, dtype=float))
