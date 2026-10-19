import pytest
from pydantic import ValidationError

from solution import make_order


def test_positive_quantity_is_kept():
    assert make_order(2).qty == 2


@pytest.mark.parametrize("bad", [0, -1])
def test_non_positive_quantity_is_rejected(bad):
    with pytest.raises(ValidationError):
        make_order(bad)
