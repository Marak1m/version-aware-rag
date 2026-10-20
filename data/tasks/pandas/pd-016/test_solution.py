import pandas as pd

from solution import flip


def test_axes_and_labels_are_exchanged():
    df = pd.DataFrame({"q1": [1, 2, 3], "q2": [4, 5, 6]}, index=["north", "south", "west"])
    out = flip(df)
    assert isinstance(out, pd.DataFrame)
    assert out.index.tolist() == ["q1", "q2"]
    assert list(out.columns) == ["north", "south", "west"]
    assert out.values.tolist() == [[1, 2, 3], [4, 5, 6]]


def test_input_is_left_unchanged():
    df = pd.DataFrame({"a": [1, 2]}, index=["x", "y"])
    flip(df)
    assert list(df.columns) == ["a"] and df.index.tolist() == ["x", "y"]
