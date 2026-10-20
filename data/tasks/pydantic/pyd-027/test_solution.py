import pytest
from pydantic import ValidationError

from solution import User, coerce_user


def test_from_a_dict():
    user = coerce_user({"id": "5", "name": "Ada"})
    assert isinstance(user, User)
    assert (user.id, user.name) == (5, "Ada")


def test_from_an_instance():
    user = coerce_user(User(id=1, name="Bo"))
    assert isinstance(user, User)
    assert (user.id, user.name) == (1, "Bo")


def test_invalid_data_is_rejected():
    with pytest.raises(ValidationError):
        coerce_user({"id": "x", "name": "Ada"})
