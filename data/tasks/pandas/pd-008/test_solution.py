import pandas as pd

from solution import fiscal_year_ends


def _fmt(idx):
    return [d.strftime("%Y-%m-%d") for d in idx]


def test_three_fiscal_year_ends_from_january():
    idx = fiscal_year_ends("2020-01-15", 3)
    assert isinstance(idx, pd.DatetimeIndex)
    assert _fmt(idx) == ["2020-06-30", "2021-06-30", "2022-06-30"]


def test_start_after_june_rolls_to_next_year():
    assert _fmt(fiscal_year_ends("2023-07-01", 2)) == ["2024-06-30", "2025-06-30"]


def test_start_on_a_fiscal_year_end_is_included():
    assert _fmt(fiscal_year_ends("2019-06-30", 1)) == ["2019-06-30"]
