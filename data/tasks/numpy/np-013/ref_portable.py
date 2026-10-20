import numpy as np


def common_dtype(dtypes):
    result = np.dtype(dtypes[0])
    for dtype in dtypes[1:]:
        result = np.promote_types(result, dtype)
    return result
