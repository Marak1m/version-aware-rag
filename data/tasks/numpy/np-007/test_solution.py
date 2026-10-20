import math

import numpy as np

from solution import mask_negatives


def test_negatives_become_nan():
    out = mask_negatives([3, -1, 2, -7])
    assert isinstance(out, np.ndarray)
    values = out.tolist()
    assert values[0] == 3.0 and values[2] == 2.0
    assert math.isnan(values[1]) and math.isnan(values[3])


def test_input_is_not_modified():
    data = np.array([-0.5, 1.5])
    out = mask_negatives(data)
    assert data.tolist() == [-0.5, 1.5]
    assert math.isnan(out.tolist()[0]) and out.tolist()[1] == 1.5


def test_zero_is_kept():
    assert mask_negatives([0, 4]).tolist() == [0.0, 4.0]
