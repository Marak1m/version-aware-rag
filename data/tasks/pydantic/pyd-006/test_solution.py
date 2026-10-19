import pytest
from pydantic import ValidationError

from solution import make_user


def test_valid_name():
    assert make_user("Ada").name.strip() == "Ada"


def test_blank_name_is_rejected():
    with pytest.raises(ValidationError):
        make_user("   ")
    with pytest.raises(ValidationError):
        make_user("")
