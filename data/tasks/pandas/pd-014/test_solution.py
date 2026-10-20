import pandas as pd

from solution import add_row


def test_row_is_appended_and_index_renumbered():
    df = pd.DataFrame({"sku": ["a1", "b2"], "qty": [3, 5]}, index=[10, 20])
    out = add_row(df, {"sku": "c3", "qty": 7})
    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == ["sku", "qty"]
    assert out.index.tolist() == [0, 1, 2]
    assert out["sku"].tolist() == ["a1", "b2", "c3"]
    assert out["qty"].tolist() == [3, 5, 7]


def test_input_is_left_unchanged():
    df = pd.DataFrame({"sku": ["a1"], "qty": [3]})
    add_row(df, {"sku": "z9", "qty": 1})
    assert len(df) == 1
    assert df["sku"].tolist() == ["a1"]
