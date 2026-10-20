import pytest
from pydantic import ValidationError

from solution import make_progress


@pytest.mark.parametrize("percent", [0, 12.5, 100])
def test_values_in_range_are_kept(percent):
    assert make_progress(percent).percent == percent


@pytest.mark.parametrize("bad", [-0.5, 100.5, 250])
def test_values_out_of_range_are_rejected(bad):
    with pytest.raises(ValidationError):
        make_progress(bad)
