import pydantic
import pytest
from pydantic import ValidationError

from solution import make_point

# Assigning to a field that cannot change raises TypeError on V1 and ValidationError on V2.
ASSIGNMENT_ERROR = TypeError if str(pydantic.VERSION).startswith("1.") else ValidationError


def test_value_is_kept():
    assert make_point(3).x == 3


def test_assignment_is_rejected():
    point = make_point(1)
    with pytest.raises(ASSIGNMENT_ERROR):
        point.x = 2
    assert point.x == 1
