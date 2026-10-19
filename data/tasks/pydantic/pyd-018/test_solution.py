import pytest
from pydantic import ValidationError

from solution import parse_scores


def test_scores_are_coerced():
    assert parse_scores(["1", 2, "30"]) == [1, 2, 30]
    assert parse_scores([]) == []


@pytest.mark.parametrize("bad", [["x"], [1, "two"], [None]])
def test_bad_scores_are_rejected(bad):
    with pytest.raises(ValidationError):
        parse_scores(bad)
