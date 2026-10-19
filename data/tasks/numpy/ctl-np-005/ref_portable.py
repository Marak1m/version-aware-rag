import numpy as np


def label_counts(labels, n_labels):
    return np.bincount(np.asarray(labels, dtype=np.intp), minlength=n_labels)
