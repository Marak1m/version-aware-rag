import pytest
from pydantic import ValidationError

from solution import make_range


def test_valid_range():
    r = make_range(1, 5)
    assert (r.lo, r.hi) == (1, 5)
    assert make_range(2, 2).hi == 2


def test_reversed_range_is_rejected():
    with pytest.raises(ValidationError):
        make_range(5, 1)
