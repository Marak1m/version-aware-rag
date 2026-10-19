import math

import numpy as np

from solution import area_under


def test_linear_curve():
    assert math.isclose(area_under(np.array([0.0, 2.0, 4.0]), np.array([0.0, 1.0, 2.0])), 4.0)


def test_nonuniform_spacing():
    assert math.isclose(area_under([1.0, 1.0, 1.0], [0.0, 1.0, 3.0]), 3.0)


def test_returns_float():
    value = area_under(np.array([0.0, 2.0]), np.array([0.0, 1.0]))
    assert isinstance(value, float)
    assert math.isclose(value, 1.0)
