from solution import Point, trusted_point


def test_values_are_stored():
    point = trusted_point(3, 4)
    assert isinstance(point, Point)
    assert (point.x, point.y) == (3, 4)


def test_no_validation_runs():
    point = trusted_point("1", "2")
    assert point.x == "1"
    assert point.y == "2"
