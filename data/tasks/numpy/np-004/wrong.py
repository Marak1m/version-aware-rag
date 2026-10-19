import numpy as np


def to_grid(values, rows, cols):
    return np.resize(np.asarray(values), (rows, cols))
