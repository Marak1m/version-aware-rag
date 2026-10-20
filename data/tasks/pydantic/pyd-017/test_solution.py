import pytest
from pydantic import ValidationError

from solution import make_plate


@pytest.mark.parametrize("good", ["AB-123", "ZZ-000"])
def test_accepts_valid_plate(good):
    assert make_plate(good).number == good


@pytest.mark.parametrize("bad", ["ab-123", "ABC-123", "AB-12", "AB-1234", "AB123", "AB-12a"])
def test_rejects_invalid_plate(bad):
    with pytest.raises(ValidationError):
        make_plate(bad)
