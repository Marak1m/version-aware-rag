import pandas as pd


def format_cells(df, fmt):
    return df.apply(lambda column: column.map(lambda x: fmt.format(x)))
