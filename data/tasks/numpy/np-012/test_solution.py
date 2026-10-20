import numpy as np

from solution import clamped_lookup


def test_in_range_positions():
    out = clamped_lookup([10, 20, 30, 40], [2, 0, 3])
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [30, 10, 40]


def test_out_of_range_positions_are_clamped():
    assert clamped_lookup([10, 20, 30], [-1, 5, 1, -4]).tolist() == [10, 30, 20, 10]
