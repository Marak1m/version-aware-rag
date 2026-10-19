import numpy as np


def moving_sum(values, window):
    return np.convolve(np.asarray(values), np.ones(window, dtype=int), mode="same")
