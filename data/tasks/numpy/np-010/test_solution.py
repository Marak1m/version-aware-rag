from solution import rows_all_positive


def test_one_flag_per_row():
    out = rows_all_positive([[1, 2, 3], [4, -5, 6]])
    assert out == [True, False]
    assert all(type(flag) is bool for flag in out)


def test_zero_is_not_positive():
    assert rows_all_positive([[0.5, 0.0], [2.0, 3.0], [-1.0, -2.0]]) == [False, True, False]
