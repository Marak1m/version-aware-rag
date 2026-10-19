import numpy as np

from solution import moving_sum


def test_full_windows_only():
    out = moving_sum([1, 2, 3, 4, 5], 3)
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [6, 9, 12]


def test_window_of_two():
    assert moving_sum([4, -1, 0, 10], 2).tolist() == [3, -1, 10]


def test_window_equal_to_length():
    assert moving_sum([2, 2, 2], 3).tolist() == [6]
