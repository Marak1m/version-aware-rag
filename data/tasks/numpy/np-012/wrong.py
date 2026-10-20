import numpy as np


def clamped_lookup(table, indices):
    table = np.asarray(table)
    return table[np.minimum(np.asarray(indices), len(table) - 1)]
