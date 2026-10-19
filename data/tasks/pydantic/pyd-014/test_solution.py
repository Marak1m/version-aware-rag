from solution import make_settings


def test_default_is_validated_to_an_integer():
    workers = make_settings({}).workers
    assert type(workers) is int
    assert workers == 4


def test_given_value_is_coerced():
    workers = make_settings({"workers": "8"}).workers
    assert type(workers) is int
    assert workers == 8
