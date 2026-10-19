from solution import to_epoch_ns


def test_nanoseconds_since_the_epoch():
    out = to_epoch_ns(["2024-03-22 11:36", "1970-01-01 00:00:01"])
    assert out == [1711107360000000000, 1000000000]
    assert all(type(v) is int for v in out)


def test_empty_input():
    assert to_epoch_ns([]) == []
