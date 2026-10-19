import pandas as pd

from solution import best_label


def test_label_of_the_maximum():
    assert best_label(pd.Series([3, 9, 1], index=["a", "b", "c"])) == "b"


def test_first_label_on_ties():
    assert best_label(pd.Series([5, 2, 5], index=["x", "y", "z"])) == "x"
