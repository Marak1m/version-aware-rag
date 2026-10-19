import numpy as np
import pytest

from solution import to_grid


def test_fills_row_by_row():
    out = to_grid([1, 2, 3, 4, 5, 6], 2, 3)
    assert isinstance(out, np.ndarray)
    assert out.shape == (2, 3)
    assert out.tolist() == [[1, 2, 3], [4, 5, 6]]


def test_single_column():
    assert to_grid(np.array([7, 8, 9]), 3, 1).tolist() == [[7], [8], [9]]


def test_size_mismatch_raises():
    with pytest.raises(ValueError):
        to_grid([1, 2, 3, 4, 5], 2, 3)
