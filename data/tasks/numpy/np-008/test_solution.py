import numpy as np

from solution import as_doubles


def test_integers_become_doubles():
    out = as_doubles([1, 2, 3])
    assert isinstance(out, np.ndarray)
    assert str(out.dtype) == "float64"
    assert out.tolist() == [1.0, 2.0, 3.0]


def test_keeps_double_precision():
    out = as_doubles([0.1, 1e-300])
    assert str(out.dtype) == "float64"
    assert out.tolist() == [0.1, 1e-300]
