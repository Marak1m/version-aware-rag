import numpy as np


def rows_all_positive(matrix):
    return np.any(np.asarray(matrix) > 0, axis=1).tolist()
