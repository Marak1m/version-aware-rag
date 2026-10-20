import pandas as pd

from solution import quarterly_totals


def _frame():
    index = pd.DatetimeIndex(["2021-01-15", "2021-03-31", "2021-04-01", "2021-06-30", "2021-11-02", "2021-12-31"])
    return pd.DataFrame({"units": [1, 2, 3, 4, 5, 6], "returns": [0, 1, 0, 0, 2, 1]}, index=index)


def test_one_row_per_quarter_labelled_by_its_last_day():
    out = quarterly_totals(_frame())
    assert isinstance(out, pd.DataFrame)
    assert [d.strftime("%Y-%m-%d") for d in out.index] == ["2021-03-31", "2021-06-30", "2021-09-30", "2021-12-31"]


def test_column_sums_with_an_empty_quarter():
    out = quarterly_totals(_frame())
    assert list(out.columns) == ["units", "returns"]
    assert out["units"].tolist() == [3, 7, 0, 11]
    assert out["returns"].tolist() == [1, 0, 0, 3]


def test_quarter_crossing_the_year():
    index = pd.DatetimeIndex(["2022-12-01", "2023-02-14"])
    out = quarterly_totals(pd.DataFrame({"units": [5, 7]}, index=index))
    assert [d.strftime("%Y-%m-%d") for d in out.index] == ["2022-12-31", "2023-03-31"]
    assert out["units"].tolist() == [5, 7]
