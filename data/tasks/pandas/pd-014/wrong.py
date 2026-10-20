import pandas as pd


def add_row(df, row):
    df.loc[len(df)] = row
    return df
