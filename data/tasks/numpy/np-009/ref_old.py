import numpy as np


def growth_path(factors):
    return np.cumproduct(np.asarray(factors))
