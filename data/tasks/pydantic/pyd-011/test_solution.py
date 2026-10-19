import pytest
from pydantic import ValidationError

from solution import make_comment


def test_short_and_exact_length_are_kept():
    assert make_comment("hello").text == "hello"
    assert make_comment("abcdefghijklmnopqrst").text == "abcdefghijklmnopqrst"


def test_longer_text_is_rejected():
    with pytest.raises(ValidationError):
        make_comment("abcdefghijklmnopqrstu")
