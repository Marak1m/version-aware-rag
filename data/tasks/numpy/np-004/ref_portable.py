import numpy as np


def to_grid(values, rows, cols):
    a = np.asarray(values)
    try:
        return np.reshape(a, shape=(rows, cols))
    except TypeError:
        # np.reshape names the argument `newshape` before the rename to `shape`.
        return np.reshape(a, newshape=(rows, cols))
