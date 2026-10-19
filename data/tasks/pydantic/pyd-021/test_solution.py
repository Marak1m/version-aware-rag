import pytest
from pydantic import ValidationError

from solution import Order, parse_order


def test_valid_json():
    order = parse_order('{"id": 3, "items": ["pen", "ink"]}')
    assert isinstance(order, Order)
    assert order.id == 3
    assert order.items == ["pen", "ink"]


def test_malformed_json_is_a_validation_error():
    with pytest.raises(ValidationError):
        parse_order('{"id": 3,')


def test_invalid_field_is_a_validation_error():
    with pytest.raises(ValidationError):
        parse_order('{"id": "x", "items": []}')
