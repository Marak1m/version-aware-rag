import pandas as pd

from solution import distinct_count


def test_missing_values_are_not_counted():
    s = pd.Series([3.0, 1.0, None, 3.0, 2.0, None])
    out = distinct_count(s)
    assert type(out) is int
    assert out == 3


def test_labels():
    assert distinct_count(pd.Series(["b", "a", "b", "b"])) == 2
