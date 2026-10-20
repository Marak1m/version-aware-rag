import pandas as pd

from solution import one_tag_per_row


def test_one_row_per_tag_with_its_label():
    tags = pd.Series([["red", "blue"], ["green"], ["red", "black", "white"]], index=["p1", "p2", "p3"])
    out = one_tag_per_row(tags)
    assert isinstance(out, pd.Series)
    assert out.tolist() == ["red", "blue", "green", "red", "black", "white"]
    assert out.index.tolist() == ["p1", "p1", "p2", "p3", "p3", "p3"]


def test_single_tags():
    out = one_tag_per_row(pd.Series([["a"], ["b"]], index=[3, 9]))
    assert out.tolist() == ["a", "b"] and out.index.tolist() == [3, 9]
