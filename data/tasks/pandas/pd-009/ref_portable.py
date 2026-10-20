import pandas as pd


def tally(s):
    return s.value_counts().rename_axis("value").reset_index(name="n")
