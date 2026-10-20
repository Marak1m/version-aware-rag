import pandas as pd

from solution import hour_marks


def test_hourly_marks_across_midnight():
    idx = hour_marks("2023-03-04 22:00", 3)
    assert isinstance(idx, pd.DatetimeIndex)
    assert [d.strftime("%Y-%m-%d %H:%M") for d in idx] == ["2023-03-04 22:00", "2023-03-04 23:00", "2023-03-05 00:00"]


def test_single_mark():
    assert [d.strftime("%H:%M") for d in hour_marks("2020-01-01 05:30", 1)] == ["05:30"]
