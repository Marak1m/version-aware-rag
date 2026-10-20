import io

import numpy as np


def read_decimal_commas(text):
    return np.loadtxt(io.StringIO(text), delimiter=";", ndmin=2)
