import math

import pandas as pd

from solution import long_form


def test_every_cell_is_kept_row_by_row():
    df = pd.DataFrame({"a": [1.0, None], "b": [2.0, 3.0]}, index=["x", "y"])
    out = long_form(df)
    assert isinstance(out, pd.Series)
    assert out.index.tolist() == [("x", "a"), ("x", "b"), ("y", "a"), ("y", "b")]
    values = out.tolist()
    assert values[0] == 1.0 and values[1] == 2.0 and values[3] == 3.0
    assert math.isnan(values[2])


def test_an_all_missing_row_survives():
    df = pd.DataFrame({"p": [None, 5.0], "q": [None, 6.0]}, index=[10, 20])
    out = long_form(df)
    assert len(out) == 4
    assert out.index.tolist() == [(10, "p"), (10, "q"), (20, "p"), (20, "q")]
    assert [math.isnan(v) for v in out.tolist()] == [True, True, False, False]
