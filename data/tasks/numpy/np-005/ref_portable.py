import numpy as np


def as_float_array(data):
    try:
        return np.array(data, dtype=np.float64, copy=None)
    except ValueError:
        # Before copy=None existed, copy=False meant "copy only if needed".
        return np.array(data, dtype=np.float64, copy=False)
