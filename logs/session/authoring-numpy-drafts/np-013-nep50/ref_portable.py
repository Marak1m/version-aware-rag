import numpy as np


def add_offset(pixels):
    return np.asarray(pixels).astype(np.uint16) + 300
