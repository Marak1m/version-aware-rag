import numpy as np


def area_under(y, x):
    return float(np.trapezoid(np.asarray(y, dtype=float), np.asarray(x, dtype=float)))
