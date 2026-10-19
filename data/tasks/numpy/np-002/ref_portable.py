import numpy as np


def code_grid(values):
    uniques, inverse = np.unique(values, return_inverse=True)
    inverse = inverse.ravel()
    return inverse.reshape(values.shape), np.bincount(inverse)
