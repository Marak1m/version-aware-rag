import numpy as np


def add_offset(pixels):
    return np.asarray(pixels).astype(np.int64) + 300
