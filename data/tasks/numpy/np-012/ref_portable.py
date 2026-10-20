import numpy as np


def clamped_lookup(table, indices):
    return np.take(np.asarray(table), indices, mode="clip")
