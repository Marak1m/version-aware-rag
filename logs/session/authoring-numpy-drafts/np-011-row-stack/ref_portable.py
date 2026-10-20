import numpy as np


def stack_rows(rows):
    return np.vstack([np.asarray(r) for r in rows])
