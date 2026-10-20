import pandas as pd

from solution import zone_of


def test_zone_name_of_a_localized_index():
    index = pd.DatetimeIndex(["2024-01-15 09:00", "2024-01-16 09:00"]).tz_localize("Europe/Paris")
    out = zone_of(index)
    assert type(out) is str
    assert out == "Europe/Paris"


def test_another_zone():
    index = pd.date_range("2023-07-01", periods=3, freq="D").tz_localize("America/New_York")
    assert zone_of(index) == "America/New_York"
