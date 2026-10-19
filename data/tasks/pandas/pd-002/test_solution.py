import pandas as pd

from solution import month_ends


def test_three_month_ends_from_mid_january():
    idx = month_ends("2020-01-15", 3)
    assert isinstance(idx, pd.DatetimeIndex)
    assert [d.strftime("%Y-%m-%d") for d in idx] == ["2020-01-31", "2020-02-29", "2020-03-31"]


def test_start_on_a_month_end_is_included():
    idx = month_ends("2021-06-30", 2)
    assert [d.strftime("%Y-%m-%d") for d in idx] == ["2021-06-30", "2021-07-31"]
