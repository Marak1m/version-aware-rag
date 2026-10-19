import numpy as np


def common_dtype(dtypes):
    return np.find_common_type(list(dtypes), [])
