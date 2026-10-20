import pytest
from pydantic import ValidationError

from solution import scale


def test_arguments_are_coerced():
    assert scale("3", "2") == 6
    assert scale(4, 5) == 20


def test_bad_argument_is_a_validation_error():
    with pytest.raises(ValidationError):
        scale("x", 2)
