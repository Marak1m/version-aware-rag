import pandas as pd


def group_ranges(df, key):
    others = [c for c in df.columns if c != key]
    return df.groupby(key)[others].apply(lambda group: group.max() - group.min())
