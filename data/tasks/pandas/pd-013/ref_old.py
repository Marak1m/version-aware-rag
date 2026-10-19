import pandas as pd


def group_ranges(df, key):
    def spread(group):
        values = group.drop(columns=key)
        return values.max() - values.min()

    return df.groupby(key).apply(spread)
