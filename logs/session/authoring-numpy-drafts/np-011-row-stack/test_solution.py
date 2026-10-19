import numpy as np

from solution import stack_rows


def test_one_row_per_sequence():
    out = stack_rows([[1, 2, 3], [4, 5, 6]])
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [[1, 2, 3], [4, 5, 6]]
