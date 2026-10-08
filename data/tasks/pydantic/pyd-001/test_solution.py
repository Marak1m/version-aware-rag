import pytest

from solution import make_sku


def test_accepts_valid_code():
    sku = make_sku("ABC-1234")
    assert sku.code == "ABC-1234"


@pytest.mark.parametrize("bad", ["abc-1234", "ABCD-1234", "ABC-123", "ABC-12345", "ABC1234", " ABC-1234"])
def test_rejects_invalid_code(bad):
    with pytest.raises(ValueError):
        make_sku(bad)
