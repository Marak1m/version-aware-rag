import pandas as pd

from solution import label_pairs


def test_labels_and_values_in_order():
    s = pd.Series([3, 1, 2], index=["red", "green", "blue"])
    assert label_pairs(s) == ["red=3", "green=1", "blue=2"]


def test_non_default_integer_labels():
    s = pd.Series(["x", "y"], index=[7, 4])
    assert label_pairs(s) == ["7=x", "4=y"]


def test_empty_series():
    assert label_pairs(pd.Series([], dtype="float64")) == []
