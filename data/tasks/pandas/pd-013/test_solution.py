import pandas as pd

from solution import group_ranges


def _frame():
    return pd.DataFrame({
        "team": ["a", "b", "a", "b", "a"],
        "x": [1, 5, 4, 2, 10],
        "y": [0.5, 1.0, 2.5, 3.0, 1.5],
    })


def test_range_per_group_for_every_other_column():
    out = group_ranges(_frame(), "team")
    assert isinstance(out, pd.DataFrame)
    assert out.index.tolist() == ["a", "b"]
    assert list(out.columns) == ["x", "y"]
    assert out["x"].tolist() == [9, 3]
    assert out["y"].tolist() == [2.0, 2.0]


def test_numeric_key_is_not_a_value_column():
    df = pd.DataFrame({"year": [2020, 2021, 2020, 2021], "sales": [3, 8, 7, 1]})
    out = group_ranges(df, "year")
    assert out.index.tolist() == [2020, 2021]
    assert list(out.columns) == ["sales"]
    assert out["sales"].tolist() == [4, 7]
