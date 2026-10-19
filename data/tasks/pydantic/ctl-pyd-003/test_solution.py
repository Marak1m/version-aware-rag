import pytest
from pydantic import ValidationError

from solution import make_rating


@pytest.mark.parametrize("stars", [1, 3, 5])
def test_ratings_in_range_are_kept(stars):
    assert make_rating(stars).stars == stars


@pytest.mark.parametrize("bad", [0, 6, -2])
def test_ratings_out_of_range_are_rejected(bad):
    with pytest.raises(ValidationError):
        make_rating(bad)
