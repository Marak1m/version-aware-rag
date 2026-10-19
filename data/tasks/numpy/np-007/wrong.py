import numpy as np


def mask_negatives(values):
    a = np.asarray(values)
    a[a < 0] = np.nan
    return a
