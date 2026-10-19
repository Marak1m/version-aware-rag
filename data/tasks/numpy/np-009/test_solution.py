import math

import numpy as np

from solution import growth_path


def test_running_product_of_integers():
    out = growth_path([2, 3, 4])
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [2, 6, 24]


def test_running_product_of_rates():
    values = growth_path([1.5, 2.0, 0.5]).tolist()
    assert len(values) == 3
    assert all(math.isclose(v, e) for v, e in zip(values, [1.5, 3.0, 1.5]))
