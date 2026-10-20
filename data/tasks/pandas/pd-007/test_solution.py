import pandas as pd

from solution import parse_stamps


def _fmt(series):
    return [d.strftime("%Y-%m-%d %H:%M:%S") for d in series]


def test_dates_with_and_without_a_time():
    out = parse_stamps(["2021-03-04", "2021-03-04T05:06:07", "2021-12-31 23:59"])
    assert isinstance(out, pd.Series)
    assert str(out.dtype).startswith("datetime64")
    assert _fmt(out) == ["2021-03-04 00:00:00", "2021-03-04 05:06:07", "2021-12-31 23:59:00"]


def test_time_first_then_plain_date():
    out = parse_stamps(["2020-02-29T12:30:00", "2020-03-01"])
    assert _fmt(out) == ["2020-02-29 12:30:00", "2020-03-01 00:00:00"]
