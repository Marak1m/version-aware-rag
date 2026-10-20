import numpy as np


def resample_linear(x_new, x, y):
    slope, intercept = np.polyfit(np.asarray(x, dtype=float), np.asarray(y, dtype=float), 1)
    return slope * np.asarray(x_new, dtype=float) + intercept
