import pandas as pd

from solution import in_range


def test_inclusive_bounds():
    out = in_range(pd.Series([1, 2, 3, 4, 5]), 2, 4)
    assert isinstance(out, pd.Series)
    assert out.tolist() == [False, True, True, True, False]


def test_index_is_kept():
    out = in_range(pd.Series([10, 20], index=["a", "b"]), 15, 25)
    assert out.index.tolist() == ["a", "b"] and out.tolist() == [False, True]
