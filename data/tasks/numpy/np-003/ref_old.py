import numpy as np


def lower_median(values):
    return float(np.percentile(values, 50, interpolation="lower"))
