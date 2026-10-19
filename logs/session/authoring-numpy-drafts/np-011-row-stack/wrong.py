import numpy as np


def stack_rows(rows):
    return np.hstack([np.asarray(r) for r in rows])
