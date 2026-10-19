import pytest
from pydantic import ValidationError

from solution import make_login


def test_long_enough_secret_is_kept():
    assert make_login("hunter22").secret == "hunter22"
    assert make_login("correct horse").secret == "correct horse"


@pytest.mark.parametrize("short", ["", "abc", "seven77"])
def test_short_secret_is_rejected(short):
    with pytest.raises(ValidationError):
        make_login(short)
