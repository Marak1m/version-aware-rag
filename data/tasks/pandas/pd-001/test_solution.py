import pandas as pd

from solution import format_cells


def test_formats_every_cell():
    df = pd.DataFrame({"a": [1, 2], "b": [3.5, 4.25]})
    out = format_cells(df, "<{}>")
    assert isinstance(out, pd.DataFrame)
    assert out.values.tolist() == [["<1>", "<3.5>"], ["<2>", "<4.25>"]]
    assert list(out.columns) == ["a", "b"]
    assert list(out.index) == [0, 1]


def test_format_spec_is_applied():
    df = pd.DataFrame({"n": [7, 42]})
    out = format_cells(df, "{:04d}")
    assert out["n"].tolist() == ["0007", "0042"]


def test_input_is_left_unchanged():
    df = pd.DataFrame({"a": [1, 2]})
    format_cells(df, "{}!")
    assert df["a"].tolist() == [1, 2]
