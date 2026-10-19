import pandas as pd


def month_ends(start, n):
    return pd.date_range(start, periods=n, freq="MS")
