import numpy as np

from solution import read_decimal_commas


def test_two_rows():
    out = read_decimal_commas("1,5;2,25\n3,0;-4,75\n")
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [[1.5, 2.25], [3.0, -4.75]]


def test_single_row_stays_two_dimensional():
    assert read_decimal_commas("0,5;10,0\n").tolist() == [[0.5, 10.0]]
