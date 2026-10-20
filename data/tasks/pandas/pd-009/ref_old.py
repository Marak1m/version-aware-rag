import pandas as pd


def tally(s):
    return s.value_counts().reset_index().rename(columns={"index": "value", s.name: "n"})
