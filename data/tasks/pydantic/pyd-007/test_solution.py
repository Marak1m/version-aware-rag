import pytest
from pydantic import ValidationError

from solution import make_cart


def test_two_items_are_enough():
    assert make_cart(["apple", "pear"]).items == ["apple", "pear"]


def test_one_item_is_rejected():
    with pytest.raises(ValidationError):
        make_cart(["apple"])
