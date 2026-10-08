import pandas as pd


def format_cells(df, fmt):
    return df.applymap(lambda x: fmt.format(x))
