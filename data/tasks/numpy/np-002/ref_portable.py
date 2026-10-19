import numpy as np


def code_grid(values):
    uniques, inverse, counts = np.unique(values, return_inverse=True, return_counts=True)
    return inverse.reshape(values.shape), counts
