import pandas as pd


def label_pairs(s):
    return [f"{label}={value}" for label, value in s.iteritems()]
