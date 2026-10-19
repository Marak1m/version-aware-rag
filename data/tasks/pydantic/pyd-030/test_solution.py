import pytest
from pydantic import ValidationError

from solution import parse_ids


def test_values_are_coerced():
    result = parse_ids(["1", 2, "3"])
    assert type(result) is list
    assert result == [1, 2, 3]


def test_invalid_item_is_a_validation_error():
    with pytest.raises(ValidationError):
        parse_ids(["1", "x"])
