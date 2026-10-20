from solution import make_reading


def test_value_is_validated():
    reading = make_reading("2.5")
    assert reading.value == 2.5
    assert make_reading(3).value == 3.0


def test_unit_stays_a_class_attribute():
    reading = make_reading(1)
    assert reading.unit.symbol == "m"
    assert type(reading).unit is reading.unit
    assert "unit" not in dict(reading)
