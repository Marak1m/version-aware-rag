import pytest
from pydantic import ValidationError

from solution import load_hook


def test_target_is_imported():
    hook = load_hook("math.sqrt")
    assert hook.target(16) == 4.0


def test_unknown_path_is_rejected():
    with pytest.raises(ValidationError):
        load_hook("math.no_such_function")
