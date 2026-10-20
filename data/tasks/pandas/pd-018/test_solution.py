import pandas as pd

from solution import days_before


def test_start_kept_end_dropped():
    idx = days_before("2022-02-26", "2022-03-02")
    assert isinstance(idx, pd.DatetimeIndex)
    assert [d.strftime("%Y-%m-%d") for d in idx] == ["2022-02-26", "2022-02-27", "2022-02-28", "2022-03-01"]


def test_one_day_span():
    assert [d.strftime("%Y-%m-%d") for d in days_before("2024-01-01", "2024-01-02")] == ["2024-01-01"]
