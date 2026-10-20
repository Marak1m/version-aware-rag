import numpy as np

from solution import common_dtype


def test_signed_and_unsigned_bytes():
    out = common_dtype(["int8", "uint8"])
    assert isinstance(out, np.dtype)
    assert str(out) == "int16"


def test_int32_and_float32_need_double():
    assert str(common_dtype([np.dtype("int32"), np.dtype("float32")])) == "float64"


def test_single_dtype_and_bool():
    assert str(common_dtype(["float32"])) == "float32"
    assert str(common_dtype(["bool", "int16"])) == "int16"
