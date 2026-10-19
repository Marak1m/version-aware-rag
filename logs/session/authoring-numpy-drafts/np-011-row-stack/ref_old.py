import numpy as np


def stack_rows(rows):
    return np.row_stack([np.asarray(r) for r in rows])
