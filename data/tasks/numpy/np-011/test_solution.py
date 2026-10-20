import numpy as np

from solution import as_float


def test_integers_become_floats():
    out = as_float([1, 2, 3])
    assert isinstance(out, np.ndarray)
    assert out.dtype.kind == "f"
    assert out.tolist() == [1.0, 2.0, 3.0]
    assert all(type(v) is float for v in out.tolist())


def test_integer_array_input():
    out = as_float(np.array([[4, 5], [6, 7]]))
    assert out.dtype.kind == "f"
    assert out.tolist() == [[4.0, 5.0], [6.0, 7.0]]
