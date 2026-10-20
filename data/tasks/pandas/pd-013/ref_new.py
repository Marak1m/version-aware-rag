import pandas as pd


def group_ranges(df, key):
    return df.groupby(key).apply(lambda group: group.max() - group.min(), include_groups=False)
