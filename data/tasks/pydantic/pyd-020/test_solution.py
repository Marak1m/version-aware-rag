import pytest
from pydantic import ValidationError

from solution import User, load_user


def test_fields_are_validated_and_coerced():
    user = load_user({"id": "7", "name": "Ada"})
    assert isinstance(user, User)
    assert user.id == 7
    assert user.name == "Ada"


def test_invalid_data_is_rejected():
    with pytest.raises(ValidationError):
        load_user({"id": "seven", "name": "Ada"})
    with pytest.raises(ValidationError):
        load_user({"id": 1})
