import pandas as pd


def quarterly_totals(df):
    return df.resample("Q").sum()
