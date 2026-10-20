import pandas as pd


def add_row(df, row):
    return df.append(row, ignore_index=True)
