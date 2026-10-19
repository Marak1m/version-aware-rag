import numpy as np

from solution import as_float_array


def test_float64_array_is_returned_as_is():
    a = np.array([1.5, 2.5, 3.5])
    out = as_float_array(a)
    assert out is a
    assert out.tolist() == [1.5, 2.5, 3.5]


def test_list_is_converted():
    out = as_float_array([1, 2, 3])
    assert isinstance(out, np.ndarray)
    assert str(out.dtype) == "float64"
    assert out.tolist() == [1.0, 2.0, 3.0]


def test_integer_array_gets_a_new_float_array():
    a = np.array([4, 5])
    out = as_float_array(a)
    assert out is not a
    assert str(out.dtype) == "float64"
    assert out.tolist() == [4.0, 5.0]
