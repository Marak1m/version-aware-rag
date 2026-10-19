from solution import lower_median


def test_even_count_picks_the_lower_middle_value():
    assert lower_median([1, 2, 3, 4]) == 2.0
    assert lower_median([10, 2, 8, 4, 6, 0]) == 4.0


def test_odd_count_is_the_middle_value():
    assert lower_median([5, 1, 3]) == 3.0
    assert type(lower_median([5, 1, 3])) is float
