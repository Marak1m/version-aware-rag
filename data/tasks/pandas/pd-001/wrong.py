import pandas as pd


def format_cells(df, fmt):
    return df.apply(lambda x: fmt.format(x))
