import numpy as np


def to_grid(values, rows, cols):
    return np.reshape(np.asarray(values), shape=(rows, cols))
