import numpy as np


def common_dtype(dtypes):
    return max((np.dtype(d) for d in dtypes), key=lambda d: d.itemsize)
