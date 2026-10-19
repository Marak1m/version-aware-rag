import numpy as np

from solution import label_counts


def test_counts_every_label():
    out = label_counts([0, 2, 2, 1, 2], 3)
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [1, 1, 3]


def test_missing_labels_count_zero():
    assert label_counts([3, 0, 3], 5).tolist() == [1, 0, 0, 2, 0]
