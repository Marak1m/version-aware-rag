import pytest
from pydantic import ValidationError

from solution import make_username


@pytest.mark.parametrize("name", ["ada", "grace_hopper", "linus"])
def test_names_of_valid_length_are_kept(name):
    assert make_username(name).name == name


@pytest.mark.parametrize("bad", ["", "al", "a_very_long_name"])
def test_names_of_invalid_length_are_rejected(bad):
    with pytest.raises(ValidationError):
        make_username(bad)
