import pytest

from solution import make_point


def test_value_is_kept():
    assert make_point(3).x == 3


def test_assignment_is_rejected():
    point = make_point(1)
    with pytest.raises((TypeError, ValueError)):
        point.x = 2
    assert point.x == 1
