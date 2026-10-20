import numpy as np


def mask_negatives(values):
    a = np.array(values, dtype=float)
    a[a < 0] = np.nan
    return a
