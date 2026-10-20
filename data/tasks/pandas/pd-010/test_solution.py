from solution import day_stamps_ns


def test_three_days_in_nanoseconds():
    out = day_stamps_ns("2020-01-01", 3)
    assert out == [1577836800000000000, 1577923200000000000, 1578009600000000000]
    assert all(type(v) is int for v in out)


def test_epoch_day():
    assert day_stamps_ns("1970-01-02", 1) == [86400000000000]
