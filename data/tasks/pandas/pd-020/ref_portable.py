import pandas as pd


def hour_marks(start, n):
    return pd.date_range(start, periods=n, freq="h")
