import math

import numpy as np

from solution import resample_linear


def test_between_points():
    out = resample_linear([0.5, 1.5, 2.25], [0.0, 1.0, 2.0, 3.0], [0.0, 10.0, 0.0, 4.0])
    assert isinstance(out, np.ndarray)
    assert all(math.isclose(v, e) for v, e in zip(out.tolist(), [5.0, 5.0, 1.0]))
    assert len(out.tolist()) == 3


def test_outside_the_range_takes_the_end_values():
    out = resample_linear([-2.0, 9.0], [0.0, 1.0, 2.0], [3.0, 5.0, 1.0]).tolist()
    assert all(math.isclose(v, e) for v, e in zip(out, [3.0, 1.0]))
    assert len(out) == 2
