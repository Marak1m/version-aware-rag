import numpy as np

from solution import add_offset


def test_no_wrap_around():
    out = add_offset(np.array([0, 200, 255], dtype=np.uint8))
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [300, 500, 555]


def test_smallest_unsigned_dtype():
    assert str(add_offset(np.array([1, 2], dtype=np.uint8)).dtype) == "uint16"
