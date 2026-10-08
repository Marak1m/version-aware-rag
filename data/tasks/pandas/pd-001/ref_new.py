import pandas as pd


def format_cells(df, fmt):
    return df.map(lambda x: fmt.format(x))
