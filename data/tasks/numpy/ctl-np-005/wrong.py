import numpy as np


def label_counts(labels, n_labels):
    _, counts = np.unique(np.asarray(labels), return_counts=True)
    return counts
