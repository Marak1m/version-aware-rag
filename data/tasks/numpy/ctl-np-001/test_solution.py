import math

import numpy as np

from solution import running_total


def test_cumulative_sum():
    out = running_total([1, 2, 3, 4])
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [1, 3, 6, 10]


def test_floats_and_negatives():
    out = running_total(np.array([0.5, -1.5, 2.0]))
    values = out.tolist()
    assert len(values) == 3
    assert all(math.isclose(v, e) for v, e in zip(values, [0.5, -1.0, 1.0]))


def test_empty_input():
    assert running_total([]).shape == (0,)
