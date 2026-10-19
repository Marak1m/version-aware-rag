import numpy as np

from solution import code_grid


def test_codes_and_counts():
    values = np.array([[3, 1], [1, 2]])
    codes, counts = code_grid(values)
    assert codes.shape == values.shape and codes.tolist() == [[2, 0], [0, 1]]
    assert counts.tolist() == [2, 1, 1]


def test_single_value():
    codes, counts = code_grid(np.array([[7, 7]]))
    assert codes.tolist() == [[0, 0]] and counts.tolist() == [2]
