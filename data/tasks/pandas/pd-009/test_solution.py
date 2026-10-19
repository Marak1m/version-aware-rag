import pandas as pd

from solution import tally


def test_counts_most_frequent_first():
    s = pd.Series(["a", "b", "b", "c", "b", "a", "c", "c", "c"], name="fruit")
    out = tally(s)
    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == ["value", "n"]
    assert out["value"].tolist() == ["c", "b", "a"]
    assert out["n"].tolist() == [4, 3, 2]
    assert out.index.tolist() == [0, 1, 2]


def test_numeric_values_and_another_name():
    s = pd.Series([7, 3, 7, 7, 3, 1], name="score")
    out = tally(s)
    assert list(out.columns) == ["value", "n"]
    assert out["value"].tolist() == [7, 3, 1]
    assert out["n"].tolist() == [3, 2, 1]
