import numpy as np

from solution import step_sizes


def test_differences():
    out = step_sizes([1, 4, 9, 16])
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [3, 5, 7]


def test_single_element_gives_empty():
    assert step_sizes([5]).shape == (0,)
