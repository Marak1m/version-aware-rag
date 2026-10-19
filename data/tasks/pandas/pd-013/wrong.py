import pandas as pd


def group_ranges(df, key):
    return df.groupby(key).transform(lambda column: column.max() - column.min())
