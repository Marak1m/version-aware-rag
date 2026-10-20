import pytest
from pydantic import ValidationError

from solution import make_account


def test_accepts_the_alias():
    assert make_account({"userName": "ada"}).user_name == "ada"


def test_accepts_the_field_name():
    assert make_account({"user_name": "bob"}).user_name == "bob"


def test_missing_value_is_rejected():
    with pytest.raises(ValidationError):
        make_account({})
