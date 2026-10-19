import numpy as np


def code_grid(values):
    result = np.unique_inverse(values)
    codes = result.inverse_indices
    return codes, np.bincount(codes.ravel())
